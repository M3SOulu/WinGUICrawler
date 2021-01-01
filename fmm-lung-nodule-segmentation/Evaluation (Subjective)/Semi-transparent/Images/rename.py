import os


index_file = open("indices.txt")
ordered_names_list = []

for x in index_file:
    if "LIDC" in x:
        ordered_names_list.append(x[6:len(x)-37])


for subdir, dirs, files in os.walk('./'):
    for file in files:
      #print("-"+file)
      if ("png") not in (file[len(file)-7:]):
          continue
      if ("fmm") in (file[len(file)-7:]):
          type = "fmm"
      elif ("ac")  in (file[len(file)-7:]):
          type = "ac"
      else:
          type = "error"
      for name in ordered_names_list:
          #print("----"+name)
          if name in file:
              new_filename = str(ordered_names_list.index(name))+"-"+type+".png"
              os.rename(file,new_filename)
              print("-> Renaming "+file+"-->"+new_filename)
