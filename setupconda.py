from cx_Freeze import setup, Executable #, version

build_exe_options = {"packages": ["cffi", "colors", "dbm", "shelve"], "excludes": ["jupyter", "scipy", "numpy","nose","email","http","html", "xml", "xmlrpc"], "include_files" : ['assets/']}
bdist_msi_options = {'add_to_path' : True}

setup(
    name ='Dementia',
    version ='0.1',
    description ='Roguelike',
    options = {"build_exe": build_exe_options, "bdist_msi": bdist_msi_options},
    executables = [Executable("main.py")],
    )