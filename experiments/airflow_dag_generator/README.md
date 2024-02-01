### What is it?
A attempt to dynamically generate dag files with the help of jinja templates.  
For every .yaml config file, a dag file is generate with the same name 

### Why?
- The dag factory approach becomes less viable at large scales.
- The better approach would be to generate the actual dag files as shown [in this youtube video](https://www.youtube.com/watch?v=_zIwdBzOYBI&t=910s)

### How to use?
Run `build_dags.py` to generate dag file 
``` py
python build_dag.py
```