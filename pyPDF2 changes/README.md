# Instalar versión modificada de pyPDF2

1. Instalar version 2.11.2 de pyPDF2

```
pip install pypdf2==2.11.2
```

2. Directorio de instalación de pyPDF2 

```
local_path=~/.local/lib/python3.10/site-packages
```

3. Dirección del parche a aplicar

```
patch_path=~/Documents/pypdf_patch/save_rectangle_in_fields.patch
```

4. Ver estado original

```
sed -n 303,307p $local_path/PyPDF2/constants.py
sed -n 317,322p $local_path/PyPDF2/constants.py
sed -n 330,322p $local_path/PyPDF2/constants.py
```

5. Aplicar parche

```
cd $local_path

git apply --stat $patch_path
git apply --check $patch_path
git apply $patch_path
```

6. Ver cambios

```
sed -n 303,308p $local_path/PyPDF2/constants.py
sed -n 318,324p $local_path/PyPDF2/constants.py
sed -n 332,339p $local_path/PyPDF2/constants.py
```
