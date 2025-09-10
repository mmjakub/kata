# Synchronize Files in Two Directories

>Imagine we want to write code for synchronizing two file directories, which we’ll call the source and the destination:
>- If a file exists in the source but not in the destination, copy the file over.
>- If a file exists in the source, but it has a different name than in the destination, rename the destination file to match.
>- If a file exists in the destination but not in the source, remove it.  
> 
><cite>[Cosmic Python](https://www.cosmicpython.com/book/chapter_03_abstractions.html#_abstracting_state_aids_testability)</cite>
 
Simple solution that does not account for cases, when files in destination need to swap places in any way.
Possible approach to fix this issue:

- build graph of overlapping `MOVE`/`COPY` operations:
    - order operations properly if graph is a tree
    - if there are cycles use temp files or copy from source (harder case)

Prevented edge case when moved/copied file that overwrites a destination file that does not exist in source(and thus 
should normally be deleted), would be deleted.  