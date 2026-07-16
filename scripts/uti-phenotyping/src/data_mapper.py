"""
Data mapper for UTI Phenotyping.
Maps manually labeled CSV data (MRN, order time, note time) back to BigQuery raw data.

Mapping Pipeline:
1. MRN → anon_id + jitter (via starr_map)
2. anon_id → cohort data + lab results (filtered by order time - jitter)
3. anon_id → notes (filtered by note time - jitter)
4. Concatenate into curated dataset
"""
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import datetime, timedelta
import logging

from .bigquery_client import BigQueryClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UTIDataMapper:
    """
    Maps labeled patient cases to raw BigQuery data for UTI phenotyping.
    
    Usage:
        mapper = UTIDataMapper()
        mapper.load_labeled_cases("path/to/labeled_cases.csv")
        curated_data = mapper.process_all_cases()
    """
    
    def __init__(self, bq_project: Optional[str] = None):
        """Initialize the data mapper."""
        self.bq_client = BigQueryClient(project=bq_project)
        self.labeled_cases: Optional[pd.DataFrame] = None
        
        # Import settings
        from config.settings import TABLES, CSV_COLUMNS, TIME_MATCH_TOLERANCE_SECONDS
        self.tables = TABLES
        self.csv_columns = CSV_COLUMNS
        self.time_tolerance = TIME_MATCH_TOLERANCE_SECONDS
    
    def load_labeled_cases(
        self, 
        csv_path: str,
        mrn_col: Optional[str] = None,
        order_time_col: Optional[str] = None,
        note_time_col: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load manually labeled cases from CSV.
        
        Args:
            csv_path: Path to the labeled CSV file
            mrn_col: Column name for MRN (uses config default if None)
            order_time_col: Column name for Urine Culture Order Date & Time
            note_time_col: Column name for Note Date/Time
            
        Returns:
            DataFrame with labeled cases
        """
        self.labeled_cases = pd.read_csv(csv_path)
        
        # Set column names from config or parameters
        self.mrn_col = mrn_col or self.csv_columns["mrn"]
        self.order_time_col = order_time_col or self.csv_columns["order_time"]
        self.note_time_col = note_time_col or self.csv_columns["note_time"]
        
        # Validate MRN column exists
        if self.mrn_col not in self.labeled_cases.columns:
            raise ValueError(f"MRN column '{self.mrn_col}' not found. Available: {list(self.labeled_cases.columns)}")
        
        logger.info(f"Loaded {len(self.labeled_cases)} labeled cases from {csv_path}")
        logger.info(f"Columns: {list(self.labeled_cases.columns)}")
        
        return self.labeled_cases
    
    # =========================================================================
    # Step 1: MRN to anon_id mapping
    # =========================================================================
    
    def get_anon_id_mapping(self, mrn: str) -> Optional[Dict[str, Any]]:
        """
        Map MRN to anon_id and jitter value.
        
        Args:
            mrn: Patient MRN from the labeled CSV
            
        Returns:
            Dict with mrn, anon_id, jitter or None if not found
        """
        query = f"""
        SELECT mrn, anon_id, jitter 
        FROM `{self.tables['mrn_map']}` 
        WHERE mrn = '{mrn}'
        """
        
        df = self.bq_client.execute_query(query)
        
        if df.empty:
            logger.warning(f"No mapping found for MRN: {mrn}")
            return None
        
        row = df.iloc[0]
        return {
            "mrn": row["mrn"],
            "anon_id": row["anon_id"],
            "jitter": row["jitter"]  # jitter in days
        }
    
    # =========================================================================
    # Step 2: Get cohort and lab data
    # =========================================================================
    
    def get_uti_cohort(self, anon_id: str) -> pd.DataFrame:
        """
        Retrieve UTI cohort data for a patient.
        
        Args:
            anon_id: Patient anonymous ID
            
        Returns:
            DataFrame with cohort data (may have multiple rows)
        """
        query = f"""
        SELECT * 
        FROM `{self.tables['uti_cohort']}` 
        WHERE anon_id = '{anon_id}'
        """
        return self.bq_client.execute_query(query)
    
    def get_lab_results(self, anon_id: str) -> pd.DataFrame:
        """
        Retrieve lab results for a patient.
        
        Args:
            anon_id: Patient anonymous ID
            
        Returns:
            DataFrame with distinct lab result times
        """
        query = f"""
        SELECT DISTINCT 
            anon_id, 
            order_time_jittered_utc, 
            taken_time_jittered 
        FROM `{self.tables['lab_result']}` 
        WHERE anon_id = '{anon_id}'
        """
        return self.bq_client.execute_query(query)
    
    def get_cohort_with_labs(
        self, 
        anon_id: str, 
        jitter_days: int,
        input_order_time: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Get cohort data and lab results, filtered by order time.
        
        Logic:
        1. Get labs where (taken_time_jittered - jitter) = input_order_time
        2. Get the order_time_jittered_utc from matched labs
        3. Filter cohort where order_time_jittered_utc matches
        
        Args:
            anon_id: Patient anonymous ID
            jitter_days: Jitter value in days from the mapping
            input_order_time: Original order time from CSV (before jitter)
            
        Returns:
            Dict with filtered cohort and labs DataFrames
        """
        # Get all lab results first
        labs_df = self.get_lab_results(anon_id)
        logger.info(f"  Retrieved {len(labs_df)} lab result rows for {anon_id}")
        
        # Get all cohort data
        cohort_df = self.get_uti_cohort(anon_id)
        logger.info(f"  Retrieved {len(cohort_df)} cohort rows for {anon_id}")
        
        # If we have an input order time, apply the filtering chain
        if input_order_time and not labs_df.empty:
            # Step 1: Filter labs where taken_time_jittered - jitter = input_order_time
            labs_df = self._filter_by_dejittered_time(
                labs_df,
                time_column="taken_time_jittered",
                jitter_days=jitter_days,
                target_time=input_order_time
            )
            logger.info(f"  After time filtering: {len(labs_df)} lab rows match")
            
            # Step 2: Get the matching order_time_jittered_utc values from labs
            if not labs_df.empty and "order_time_jittered_utc" in labs_df.columns:
                matching_order_times = labs_df["order_time_jittered_utc"].dropna().unique()
                logger.info(f"  Found {len(matching_order_times)} unique order times from labs")
                
                # Step 3: Filter cohort by matching order_time_jittered_utc
                if not cohort_df.empty and "order_time_jittered_utc" in cohort_df.columns:
                    cohort_df["order_time_jittered_utc"] = pd.to_datetime(
                        cohort_df["order_time_jittered_utc"], errors='coerce'
                    )
                    matching_order_times = pd.to_datetime(matching_order_times)
                    
                    # Match within a small tolerance (1 minute)
                    def matches_any_order_time(t):
                        if pd.isna(t):
                            return False
                        for mt in matching_order_times:
                            if abs((t - mt).total_seconds()) < 60:
                                return True
                        return False
                    
                    mask = cohort_df["order_time_jittered_utc"].apply(matches_any_order_time)
                    cohort_df = cohort_df[mask]
                    logger.info(f"  After order_time matching: {len(cohort_df)} cohort rows match")
        
        return {
            "cohort": cohort_df,
            "labs": labs_df
        }
    
    # =========================================================================
    # Step 3: Get notes
    # =========================================================================
    
    def get_uti_notes(
        self, 
        anon_id: str,
        jitter_days: int,
        input_note_time: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieve notes for a patient, filtered by de-jittered time.
        
        The input_note_time should match: notedatetime_utc - jitter - UTC_offset
        
        Args:
            anon_id: Patient anonymous ID
            jitter_days: Jitter value in days
            input_note_time: Original note time from CSV (in local time, before jitter)
            
        Returns:
            DataFrame with notes matching the time criteria
        """
        query = f"""
        SELECT * 
        FROM `{self.tables['uti_notes']}` 
        WHERE anon_id = '{anon_id}'
        """
        
        notes_df = self.bq_client.execute_query(query)
        logger.info(f"  Retrieved {len(notes_df)} notes for {anon_id}")
        
        # Filter by de-jittered note time if provided
        if input_note_time and not notes_df.empty:
            # Try common column names for note datetime
            time_col = self._find_datetime_column(notes_df, ["notedatetime", "notedatetime_utc", "note_datetime_utc", "note_date_jittered"])
            if time_col:
                logger.info(f"  Using time column: {time_col}")
                # Note: notedatetime is in UTC, input_note_time is in local time
                # So we need to convert UTC to local after dejittering
                notes_df = self._filter_by_dejittered_time(
                    notes_df,
                    time_column=time_col,
                    jitter_days=jitter_days,
                    target_time=input_note_time,
                    convert_utc_to_local=True  # Convert UTC to Pacific time
                )
                logger.info(f"  After time filtering: {len(notes_df)} notes match")
            else:
                logger.warning(f"  Could not find datetime column in notes. Available: {list(notes_df.columns)}")
        
        return notes_df
    
    # =========================================================================
    # Helper methods for time filtering
    # =========================================================================
    
    def _find_datetime_column(self, df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
        """Find the first matching datetime column from candidates."""
        for col in candidates:
            if col in df.columns:
                return col
        # Try case-insensitive match
        df_cols_lower = {c.lower(): c for c in df.columns}
        for col in candidates:
            if col.lower() in df_cols_lower:
                return df_cols_lower[col.lower()]
        return None
    
    def _filter_by_dejittered_time(
        self,
        df: pd.DataFrame,
        time_column: str,
        jitter_days: int,
        target_time: str,
        convert_utc_to_local: bool = False
    ) -> pd.DataFrame:
        """
        Filter DataFrame rows where (time_column - jitter) matches target_time.
        
        Args:
            df: DataFrame to filter
            time_column: Column containing jittered datetime (may be in UTC)
            jitter_days: Jitter in days to subtract
            target_time: Target datetime string to match (assumed local time)
            convert_utc_to_local: If True, convert UTC to Pacific time before comparing
            
        Returns:
            Filtered DataFrame
        """
        if df.empty or time_column not in df.columns:
            return df
        
        # Convert target time to datetime
        try:
            target_dt = pd.to_datetime(target_time)
            # Make target timezone-naive for comparison
            if target_dt.tzinfo is not None:
                target_dt = target_dt.tz_localize(None)
        except Exception as e:
            logger.warning(f"Could not parse target time '{target_time}': {e}")
            return df
        
        # Ensure the time column is datetime
        df = df.copy()
        df[time_column] = pd.to_datetime(df[time_column], errors='coerce')
        
        # Calculate de-jittered time
        jitter_delta = pd.Timedelta(days=jitter_days)
        df['_dejittered_time'] = df[time_column] - jitter_delta
        
        # Convert UTC to Pacific time if needed (UTC-7 or UTC-8 depending on DST)
        if convert_utc_to_local:
            # Subtract 7 hours for Pacific Daylight Time (summer)
            # This is approximate - for more accuracy, use pytz
            df['_dejittered_time'] = df['_dejittered_time'] - pd.Timedelta(hours=7)
        
        # Remove timezone info for comparison
        df['_dejittered_time'] = df['_dejittered_time'].dt.tz_localize(None)
        
        # Log for debugging
        logger.info(f"  Target time: {target_dt}")
        logger.info(f"  De-jittered times: {df['_dejittered_time'].tolist()}")
        
        # Match within tolerance (within 1 hour for more precision)
        tolerance = pd.Timedelta(hours=1)
        mask = abs(df['_dejittered_time'] - target_dt) <= tolerance
        
        logger.info(f"  Matching mask: {mask.tolist()}")
        
        result = df[mask].drop(columns=['_dejittered_time'])
        return result
    
    # =========================================================================
    # Main processing methods
    # =========================================================================
    
    def process_single_case(
        self,
        mrn: str,
        order_time: Optional[str] = None,
        note_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single labeled case through the full mapping pipeline.
        
        Args:
            mrn: Patient MRN from CSV
            order_time: Urine Culture Order Date & Time from CSV
            note_time: Note Date/Time from CSV
            
        Returns:
            Dictionary containing all mapped data including final concatenated DataFrame
        """
        result = {
            "mrn": mrn,
            "input_order_time": order_time,
            "input_note_time": note_time,
            "mapping": None,
            "cohort": pd.DataFrame(),
            "labs": pd.DataFrame(),
            "notes": pd.DataFrame(),
            "final_df": pd.DataFrame(),  # Concatenated cohort + notes
            "error": None
        }
        
        # Step 1: Get anon_id mapping
        logger.info(f"Processing MRN: {mrn}")
        mapping = self.get_anon_id_mapping(mrn)
        
        if mapping is None:
            result["error"] = f"No anon_id mapping found for MRN: {mrn}"
            return result
        
        result["mapping"] = mapping
        anon_id = mapping["anon_id"]
        jitter = mapping["jitter"]
        
        logger.info(f"  Mapped to anon_id: {anon_id}, jitter: {jitter} days")
        
        # Step 2: Get cohort and lab data (filtered by order_time)
        cohort_labs = self.get_cohort_with_labs(
            anon_id=anon_id,
            jitter_days=jitter,
            input_order_time=order_time
        )
        result["cohort"] = cohort_labs["cohort"]
        result["labs"] = cohort_labs["labs"]
        
        # Step 3: Get notes (filtered by note_time)
        result["notes"] = self.get_uti_notes(
            anon_id=anon_id,
            jitter_days=jitter,
            input_note_time=note_time
        )
        
        # Step 4: Create final concatenated DataFrame
        result["final_df"] = self._create_final_df(
            mrn=mrn,
            order_time=order_time,
            note_time=note_time,
            cohort_df=result["cohort"],
            notes_df=result["notes"]
        )
        
        return result
    
    def _create_final_df(
        self,
        mrn: str,
        order_time: Optional[str],
        note_time: Optional[str],
        cohort_df: pd.DataFrame,
        notes_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Create the final merged DataFrame for a single case.
        
        Combines cohort data + notes data into a single row per case.
        If multiple cohort rows or multiple notes, they are joined.
        
        Args:
            mrn: Patient MRN
            order_time: Input order time
            note_time: Input note time
            cohort_df: Filtered cohort data
            notes_df: Filtered notes data
            
        Returns:
            Merged DataFrame with cohort + notes combined horizontally
        """
        # Start with cohort data
        if not cohort_df.empty:
            final_df = cohort_df.copy()
            logger.info(f"  Starting with {len(final_df)} cohort rows")
        else:
            final_df = pd.DataFrame()
        
        # Add notes columns to cohort data
        if not notes_df.empty:
            # Get note-specific columns (exclude common columns to avoid duplication)
            common_cols = ["anon_id", "encounterid", "order_proc_id_coded"]
            note_specific_cols = [c for c in notes_df.columns if c not in common_cols]
            
            if not final_df.empty:
                # Merge notes into cohort based on common columns
                # If there are multiple notes, combine them
                if len(notes_df) == 1:
                    # Single note - just add the columns
                    for col in note_specific_cols:
                        final_df[col] = notes_df[col].iloc[0]
                else:
                    # Multiple notes - combine note text with separator
                    combined_note_text = "\n\n---NOTE SEPARATOR---\n\n".join(
                        notes_df["deid_note_text"].dropna().astype(str).tolist()
                    )
                    combined_note_types = ", ".join(
                        notes_df["note_type"].dropna().astype(str).unique().tolist()
                    )
                    combined_note_times = ", ".join(
                        notes_df["notedatetime"].dropna().astype(str).tolist()
                    )
                    
                    final_df["notedatetime"] = combined_note_times
                    final_df["deid_note_text"] = combined_note_text
                    final_df["note_type"] = combined_note_types
                    
                logger.info(f"  Merged {len(notes_df)} notes into cohort")
            else:
                # No cohort data, use notes as base
                final_df = notes_df.copy()
                logger.info(f"  Using {len(final_df)} notes rows (no cohort data)")
        
        if final_df.empty:
            logger.warning(f"  No data for MRN {mrn}")
            return pd.DataFrame()
        
        # Add metadata columns
        final_df["mrn"] = mrn
        final_df["input_order_time"] = order_time
        final_df["input_note_time"] = note_time
        
        # Reorder columns: put mrn, input_order_time, input_note_time at the front
        priority_cols = ["mrn", "input_order_time", "input_note_time"]
        other_cols = [c for c in final_df.columns if c not in priority_cols]
        final_df = final_df[priority_cols + other_cols]
        
        logger.info(f"  Final DataFrame has {len(final_df)} rows")
        
        return final_df
    
    def process_all_cases(
        self,
        output_dir: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Process all labeled cases and return curated dataset.
        
        Args:
            output_dir: Optional directory to save results
            
        Returns:
            List of result dictionaries for each case
        """
        if self.labeled_cases is None:
            raise ValueError("No labeled cases loaded. Call load_labeled_cases() first.")
        
        all_results = []
        
        for idx, row in self.labeled_cases.iterrows():
            mrn = str(row[self.mrn_col])
            
            # Get order time and note time (handle missing columns gracefully)
            order_time = None
            note_time = None
            
            if self.order_time_col in row.index and pd.notna(row[self.order_time_col]):
                order_time = str(row[self.order_time_col])
            
            if self.note_time_col in row.index and pd.notna(row[self.note_time_col]):
                note_time = str(row[self.note_time_col])
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Case {idx + 1}/{len(self.labeled_cases)}")
            
            result = self.process_single_case(
                mrn=mrn,
                order_time=order_time,
                note_time=note_time
            )
            
            # Add original row data
            result["original_row"] = row.to_dict()
            all_results.append(result)
        
        # Save results if output directory provided
        if output_dir:
            self._save_results(all_results, output_dir)
        
        return all_results
    
    def create_curated_dataset(
        self, 
        results: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Create a curated dataset by concatenating final_df from all cases.
        
        Each case's final_df contains matched cohort + notes data.
        
        Args:
            results: List of results from process_all_cases()
            
        Returns:
            Concatenated DataFrame with all data
        """
        curated_rows = []
        
        for result in results:
            if result.get("error"):
                continue
            
            # Use the pre-computed final_df which has matched cohort + notes
            final_df = result.get("final_df", pd.DataFrame())
            if not final_df.empty:
                curated_rows.append(final_df)
        
        if not curated_rows:
            logger.warning("No data to curate")
            return pd.DataFrame()
        
        # Concatenate all data
        curated_df = pd.concat(curated_rows, ignore_index=True)
        logger.info(f"Created curated dataset with {len(curated_df)} rows")
        
        return curated_df
    
    def _save_results(self, results: List[Dict], output_dir: str):
        """Save processing results to output directory."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save summary
        summary_rows = []
        for r in results:
            summary_rows.append({
                "mrn": r["mrn"],
                "input_order_time": r.get("input_order_time"),
                "input_note_time": r.get("input_note_time"),
                "anon_id": r["mapping"]["anon_id"] if r["mapping"] else None,
                "jitter": r["mapping"]["jitter"] if r["mapping"] else None,
                "matched_cohort_rows": len(r["cohort"]) if isinstance(r["cohort"], pd.DataFrame) else 0,
                "matched_lab_rows": len(r["labs"]) if isinstance(r["labs"], pd.DataFrame) else 0,
                "matched_note_rows": len(r["notes"]) if isinstance(r["notes"], pd.DataFrame) else 0,
                "final_df_rows": len(r["final_df"]) if isinstance(r.get("final_df"), pd.DataFrame) else 0,
                "error": r.get("error")
            })
        
        summary_df = pd.DataFrame(summary_rows)
        summary_df.to_csv(output_path / "mapping_summary.csv", index=False)
        logger.info(f"Saved mapping summary to {output_path / 'mapping_summary.csv'}")
        
        # Create and save curated dataset (concatenation of all final_df)
        curated_df = self.create_curated_dataset(results)
        if not curated_df.empty:
            curated_df.to_csv(output_path / "curated_dataset.csv", index=False)
            logger.info(f"Saved curated dataset to {output_path / 'curated_dataset.csv'}")
