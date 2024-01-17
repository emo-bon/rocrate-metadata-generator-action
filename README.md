# rocrate-metadata-generator-action

Example workflow file:

```
on:
  push:
jobs:
  job0:
    runs-on: ubuntu-latest
    steps:
      - name: checkout
        uses: actions/checkout@v3
      - name: rocrate-metadata-generator-action
        uses: emo-bon/rocrate-metadata-generator-action@main
        env:
          PROFILE: https://data.emobon.embrc.eu/observatory-profile/0.1
          REPO: ${{ github.repository }}
      - name: commit
        uses: stefanzweifel/git-auto-commit-action@v4
```
