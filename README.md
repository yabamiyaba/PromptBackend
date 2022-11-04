"stability-sdk" must be cloned by https://github.com/Stability-AI/stability-sdk
and need to change some files and setup
1. setup in venv dependencices
2. stability-sdk/src/stability_sdk/__main__.py", line 158  
    "cli_args" valiables are not difined, so cli_args => args
3. stability-sdk/src/stability_sdk/__main__.py", line 177  
    process_artifacts_from_answers is not imported, so add "from stability_sdk.client import process_artifacts_from_answers"
4. set your API keys  
    1. views.py line56  
    set Stability Key  
    2. views.py line67  
    set Imgur client id
