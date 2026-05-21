[![Built with Material for MkDocs](https://img.shields.io/badge/Material_for_MkDocs-526CFE?style=for-the-badge&logo=MaterialForMkDocs&logoColor=white)](https://squidfunk.github.io/mkdocs-material/)

```powershell
python -m venv venv
./venv/Scripts/Activate.ps1

./python-path.ps1
Get-ChildItem plugins | ForEach-Object { pip install -e $_.FullName }
pip install -r requirements.txt
pip install mkdocs-material[recommended]

mkdocs serve --watch-theme
```
