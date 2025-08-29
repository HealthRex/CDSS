# Virtual Environment Setup for DSPy Clinical Communication Project

This document explains how to set up and use the virtual environment for the DSPy-based clinical communication error identification project.

## Environment Setup

### 1. Virtual Environment
The project uses a Python virtual environment named `inbasket_env` to manage dependencies.

### 2. Dependencies
The following key packages are installed:
- **dspy-ai**: Core DSPy framework for AI/LLM applications
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning utilities
- **asyncio**: Asynchronous programming support
- **pydantic**: Data validation
- **openai**: OpenAI API integration
- **python-dotenv**: Environment variable management

## Usage

### Activating the Environment

**Option 1: Use the activation script**
```bash
./activate_env.sh
```

**Option 2: Manual activation**
```bash
source inbasket_env/bin/activate
```

### Running the Project

Once the environment is activated, you can run the main script:
```bash
python src/main_DSPy.py
```

### Deactivating the Environment

When you're done working:
```bash
deactivate
```

## Project Structure

```
Embedding_Pilot_Exp/
├── inbasket_env/           # Virtual environment
├── src/                    # Source code
│   ├── main_DSPy.py       # Main DSPy script
│   ├── data/              # Data loading utilities
│   ├── util/              # Utility modules
│   └── ...
├── requirements.txt        # Dependencies list
├── activate_env.sh        # Environment activation script
└── README_ENV.md          # This file
```

## Troubleshooting

### If you get import errors:
1. Make sure the virtual environment is activated (you should see `(inbasket_env)` in your prompt)
2. Check that all dependencies are installed: `pip list`
3. Reinstall dependencies if needed: `pip install -r requirements.txt`

### If you need to recreate the environment:
```bash
rm -rf inbasket_env
python3 -m venv inbasket_env
source inbasket_env/bin/activate
pip install -r requirements.txt
```

## Notes

- The environment uses Python 3.9
- All dependencies are pinned to specific versions for reproducibility
- The project is designed for clinical communication error identification using DSPy
