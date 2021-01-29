import os

for subdir, dirs, files in os.walk('./'):
    files.sort()
    print("\\begin{table}[]")
    print("\\begin{tabular}{ll}")
    print("\\hline")
    print("\\multicolumn{1}{|l|}{Case}          & \\multicolumn{1}{l|}{Diameter} \\\\ \\hline")
    for file in files:
        if file[:4] == "LIDC":
            ciccio = file[:-4]
            print("\\multicolumn{1}{|l|}{"+file[:14]+"}          & \\multicolumn{1}{l|}{"+ciccio[15:]+"} \\\\ \\hline")
print("\\end{tabular}")
print("\\end{table}")
