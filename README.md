# ghas-sarif-puller

GitHub Advanced Security to pull the SARIF

## Usage

```bash
# Install dependencies
pipenv install

# Run help
pipenv run python ./ghas-sarif-puller.py --help
```

~~~
 usage: GHAS-SARIF-Puller [-h] [--debug] -r REPOSITORY [-t TOKEN] [--ref REF] [-o OUTPUT]
 
 optional arguments:
   -h, --help            show this help message and exit
   --debug               Enable Debugging
 
 GitHub:
   -r REPOSITORY, --repository REPOSITORY
                         Repository full name (org/repo)
   -t TOKEN, --token TOKEN
                         GitHub PAT (default: $GITHUB_TOKEN)
   --ref REF             Git Reference / Branch (refs/heads/<branch name>)
 
 SARIF:
   -o OUTPUT, --output OUTPUT
~~~

### Example Command

```bash
pipenv run python ./ghas-sarif-puller.py \
    -r "GeekMasher/Pixi" \
    -o "geekamsher-pixi.sarif"
```
