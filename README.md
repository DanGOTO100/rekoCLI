# rekoCLI
RekoCLI is a custom python lightweight CLI sitting on top of Amazon Rekognition CLI.
It provides with hgigher level of abstraction commands and easier to read output. 
Facilitates better demos and more insights on the results.
It leverages "cmd" package to create a nice CLI interface flow.

This CLI can run on any EC2 instance where AWS CLI lives and any other Linux with AWS CLI
Check [Amazon Rekognition](https://aws.amazon.com/rekognition/) if you are not familiar with this image/video metadata extraction service.

# Available Commands:

List of avaialble commands in the tool. You can always use command help to get number/type of arguments and useful information.

**coll:** List collections

**newcoll:** Create new collection

**listfaces:** list faces in a collection

**addface:** add faces to a collection

**startface:** start face analysis job

**resultface:** get results from a face analysis job

**startlabel:** start label detection job of a given video

**resultlabel:** get the results from a label detection job

**starttrack:** start a tracking job

**resulttrack** get the the results from a tracking job

**q** exits the CLI

# Extra Notes

   Before using this CLI:
   
    1) Configure AWS CLI tool with your region.
    
    2)Make sure your instance has a role to allow rekognition and S3 permission 
    
    3)Make sure you have a bucket with the images, videos and a SNS Topic ARN and its ServiceRole ARN ready, all in the same region. Enjoy!!\n')
