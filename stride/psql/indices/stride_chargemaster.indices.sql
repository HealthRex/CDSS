-- Table: stride_chargemaster

CREATE INDEX IF NOT EXISTS index_stride_chargemaster_service_code
                            ON stride_chargemaster(service_code);
