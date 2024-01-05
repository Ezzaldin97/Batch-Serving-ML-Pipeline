# DVC Training Pipeline:

DVC is the Git of **Data**, it is originally designed to track your data, artifacts, and models using the same concepts of Git to track your code.

Github, Gitlab, and other platform that are used for code-versioning, isn't designed for large-amount of data/models/artifacts that are input/results of machine learning development process, so it is very important to find something that give us the same advantage to track our data to make it accessable, sharable between team members, and versioned, DVC gives us this advantage, we can use remote/local storage (file-system/S3/HDFS) to store data/artifacts, and use DVC to push & pull data just like code with Git

![](../../imgs/dvc-versioning.PNG)

to start tracking files on your project:

```bash
dvc init
```

after intializing DVC, all data/artifacts/models will be tracked, no you can start adding files:

```bash
dvc add .
```
adding files to DVC will create metadata files for all files that added to DVC, and add them to .gitignore.

intializing DVC will add .dvc, you must add & commit to git as well:

```bash
git add .
git commit -m "your message...."
```

now, let's configure the remote/local storage that will be used to store all files added to DVC:

```bash
# i used local storage in this project.
# first it created a directory on my machine using mkdir command, then used the following
dvc remote add -d localremote 'path/path_of_dir'
```

no push your files to remote/local stoarge:

```bash
dvc push
```

