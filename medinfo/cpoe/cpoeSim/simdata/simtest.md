#### Steps to Reproduce Database

- insert stride tables 2014

STEP 1

- make sure you update your Postgres connection at the top of the system for restoreSimTables and restoreSimTables

STEP 2
- run revertSimTables.sh "./revertSimTables.sh"


##### Testing Chemo Fever 2:
Things to Test


|Action   | Result   |   
|---   |---       |
|amoxicillin      | state doesn't change      |    
|doxycline        | state doesn't change      |   
|cephalexin       | state doesn't change      |    
|ciprofloxacin    | state doesn't change      |
|Glucose-Piperacillin-Tazobactam    |state doesn't change   |   
|cefepime         | state -> 5001             |   
|lactated ringers | 5000 -> 5002              |   
|Sodium-Chloride  | 5000 -> 5001              |   
|Zosyn            |   |   
|Meropenem        |5000 -> 5001   |   
|Aztreonam        | 5000 -> 5001   |   
|Ceftazidime      | 5000 -> 5001    |   
|Ceftazidime -> IVF | 5000 -> 5001 -> 5003    |    
|Zosyn2           |    |
|Aztreonam + NS IVF      | 5000 -> 5001 + 5003       |  
|NS IVF -> Moropenum   | 5000 -> 5002 -> 5003        |     
|cefepime + IVF   | 5000 -> (5001,5003)              |   
|Aztreonam + IVF   | 5000 -> (5001,5003)             |   
|Lactated Ringers  + Cefepime  | 5000 -> (5002,5003) |
|Lactated Ringers + Meropenum   |5000 -> (5002,5003) |

#### Meningitis (Neck Stiffness) Testing

|Action   | Result   |   
|---   |---       |
|Ceftriaxone  (intravenous)   | 30 -> 31      |    
|cefepime         | 30 -> 31             |   
|Meropenem        | 30 -> 31 |   
|Do nothing for two hours        | 30 -> 32 -> 33|   

