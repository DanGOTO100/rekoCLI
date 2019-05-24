# rekoCLI
RekoCLI is a custom python lightweight CLI sitting on top of Amazon Rekognition CLI.
It provides with simpler commands and easier to read output. 
Facilitates better demos and more insights on the results.
It leverages "cmd" package to create a nice CLI interface flow.

Check Amazon Rekognition if you are not familiar with this image/video metadata extraction service.

# Available Commands:

** coll: ** List collections
** newcoll: ** Create new collection
** listfaces: ** list faces in a collection
** addface: ** add faces to a collection
** startface: ** start face analysis job
** resultface: ** get results from a face analysis job

** startlabel: ** start label detection job of a given video
** resultlabel: ** get the results from a label detection job
** starttrack: ** start a tracking job
** resulttrack ** get the the results from a tracking job
** q ** exits the CLI
