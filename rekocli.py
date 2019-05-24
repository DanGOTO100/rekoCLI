#    Before using this CLI:
#    1) Configure AWS CLI tool with your region.
#    2)Make sure your instance has a role to allow rekognition and S3 permission 
#    3)Make sure you have a bucket with the images, videos and a SNS Topic ARN and its ServiceRole ARN ready, all in the same region. Enjoy!!\n')



from cmd import Cmd
import os
import boto3
import json

client = boto3.client('rekognition')



# lastjob initialized to 0, as no job scheduled yet and boto3 needs regular expression pattern: ^[a-zA-Z0-9-_]+$
lastjob = 0

class MyPrompt(Cmd):

    def do_coll(self,args):
        """List current collections in the region"""
        response = client.list_collections()
        print(json.dumps(response['CollectionIds']))
        return

    def do_newcoll(self,args):
        """Create a collection in the region.Needs name of the collection as an argument. """
        if len(args) == 0:
            print("CollectionId is missing. Use help, it is your friend")
            return
        cid=args.split()
        response = client.create_collection(
            CollectionId=cid[0]
        )
        print(json.dumps(response,indent=2,sort_keys=True))
        return

    def do_q(self, args):
        """Close the CLI and goes back to command prompt"""
        print("Thank you for using this tool. See you next time!")
        raise SystemExit


    def do_listfaces(self, args):
        """Lists the faces already in the collection id passed as an argument"""
        if len(args) == 0:
            print("CollectionId is missing. Use help, it is your friend")
        else:
            cid = args.split()
            print("Collection ID requested: ",cid[0])
            response = client.list_faces(
            CollectionId=cid[0])
            print(json.dumps(response['Faces'],indent=4, sort_keys=True))

    def do_addface(self, args):
        """Add a face in a collection. Usage: add collectionid S3Bucket Imagename ExtimageId"""
        if len(args) == 0:
            print("Arguments missing for adding to the collection. Needs 4 arguments. Help is your friend.")
        else:
            cid = args.split()
            if len(cid) <4:
                print("Arguments missing. We need 4 arguments")
                return
            print("Collection ID to add to: ", cid[0])
            print("S3Bucket name: ", cid[1])
            print("Image to add: ",cid[2])
            print("ExternalID for the image: ",cid[3])
            print("")

            response = client.index_faces(
                CollectionId=cid[0],
                Image={
                        'S3Object': {
                        'Bucket': cid[1],
                        'Name': cid[2],
                        }
                },
                ExternalImageId=cid[3],
            )
            print(json.dumps(response,indent=4, sort_keys =True))

    def do_startface(self, args):
        """Starts analysis of a stored video. Face Threshold set to 75. Usage: startface collectionid S3Bucket videoname SNSTopic ARNRole. """
        if len(args) == 0:
            print("Arguments missing for analyzing the video. Needs 5 arguments. Help is your friend.")
        else:
            cid = args.split()
            if len(cid) <5:
                print("Arguments missing. We need 5 arguments")
                return
            print("Collection ID to check: ", cid[0])
            print("S3Bucket name: ", cid[1])
            print("Video to analyze: ", cid[2])
            print("SNS ARN", cid[3])
            print("ARN Role",cid[4])
            print("")

            response=client.start_face_search(
                    Video={
                        'S3Object': {
                            'Bucket': cid[1],
                            'Name': cid[2],
                        }
                    },
                    FaceMatchThreshold=75,
                    CollectionId= cid[0],
                    NotificationChannel={
                        'SNSTopicArn': cid[3],
                        'RoleArn': cid[4]
                    },
                    JobTag='Jobrekdemo'
                )
            print(response)
            print("--------------------------------------------")
            lastjob=json.dumps(response['JobId'])
            print("JobID generated to track is: ",lastjob)
            f = open('joblogfile', 'a')
            f.write(lastjob)
            f.write(args)
            f.write('\n')
            f.close 
            return


    def do_resultface(self, args):
        """ Prints the result of the face analysis needs jobId and max. results."""
        summary = []
        cid = args.split()
        if len(cid) <  2:
            lastjob = os.getenv('JOBID')
            print("No jobID or Max results given. Need JobId and number of results")
            return
        else:
            cid = args.split()
            print("JobID: ", cid[0])
            print("MaxResults", cid[1])
        response = client.get_face_search(
            JobId=cid[0],
            MaxResults=int(cid[1])
        )
        responsej = json.dumps(response, indent=4, sort_keys =True)            
        f = open('job-faces-output', 'w')
        f.write(responsej)
        f.close 
        #Here check if job still in progress, if so, print the output and getout.
        if  not response['Persons']:
            print(responsej)
            return
        #If here, job is completed, print response.
        long=len(response['Persons'])
        fx = open('faceoutput.csv','w')
        fx.close()
        
        for res in range(0, long):
            b = response['Persons'][res].get('FaceMatches','')
            bb = response['Persons'][res].get('Person','')
            c = json.dumps(b)
            if len(b) > 0:
                print("------------Face detected: ",b[0]['Face']['ExternalImageId']," ---------------------")
                print("Timestamp: ",response['Persons'][res].get('Timestamp',"No time"))
                print("ExternalImageId detected: ",b[0]['Face']['ExternalImageId']," with faceid: ",b[0]['Face']['FaceId']," and confidence: ",b[0]['Face']['Confidence'])
                print("--------------------------------------------------------")
                print("")
                summary.append(b[0]['Face']['ExternalImageId'])
                
                #extract coordenates to export to numpy and OpenCSV
                print(">>> ",bb)
                cx=bb['Face']['BoundingBox']['Left']
                cy=bb['Face']['BoundingBox']['Top']
                cx2=bb['Face']['BoundingBox']['Width']
                cy2=bb['Face']['BoundingBox']['Height']

                #extract confidence value 
                conf=b[0]['Similarity']
                
                #logging to CSV for OpenCSV later analysis, loading into numpy
                fx = open('faceoutput.csv','a')
                linetowrite = str(response['Persons'][res].get('Timestamp',"No time")) + "," + str(cx) + "," + str(cy) + "," + str(cx2) + "," + str(cy2) + "," + str(conf) + "\n"
                fx.write(linetowrite)
            
        fx.close            
        summaryt = [ (summary.count(x), x) for x in set(summary)]
        print("*****************************************************")
        print("SUMMARY: External FaceID detected and its occurrences:")
        print(summaryt)
        print("\n Using default value for result gathering: 1000")
        print("\n ** Full job out in JSON format in file job-faces-output **")
        
        #Automatically upload the csv file to my S3 bucket.
        data=open('faceoutput.csv','rb')
        s3 = boto3.resource('s3')
        s3.Bucket('--your-bucket--').put_object(Key='faceoutput.csv', Body=data)

    def do_startlabel(self, args):
        """Starts label detecteion analysis of a stored video.  Usage: startlabel S3Bucket videoname SNSTopic ARNRole. """
        if len(args) == 0:
            print("Arguments missing for analyzing the video. Needs 4 arguments. Help is your friend.")
        else:
            cid = args.split()
            if len(cid) <4:
                print("Arguments missing. We need 4 arguments")
                return
            print("S3Bucket name: ", cid[0])
            print("Video to analyze: ", cid[1])
            print("SNS ARN", cid[2])
            print("ARN Role",cid[3])
            print("")

            response=client.start_label_detection(
                    Video={
                        'S3Object': {
                            'Bucket': cid[0],
                            'Name': cid[1],
                        }
                    },
                    NotificationChannel={
                        'SNSTopicArn': cid[2],
                        'RoleArn': cid[3]
                    },
                )
            print(json.dumps(response,indent=4,sort_keys=True))
            print("--------------------------------------------")
            lastjob=json.dumps(response['JobId'])
            print("JobID generated to track is: ",lastjob)
            f = open('joblogfile', 'a')
            f.write(lastjob)
            f.write(args)
            f.write('\n')
            f.close
            return

    def do_resultlabel(self, args):
        """ Prints the result of the analysis of the  label detection job, jobId  is needed, """
        summary = []
        if len(args) == 0:
            lastjob = os.getenv('JOBID')
            print("No jobID given. Need JobId")
            print(response)
        else:
            cid = args.split()
            print("JobID: ", cid[0])
        response = client.get_label_detection(
            JobId=cid[0],
        )
        #Job in progress? Show it and getout
        if not response['Labels']:
            print(json.dumps(response,indent=4,sort_keys=True))
            return
        
        #Job finished
        print("LEN..",len(response['Labels']))
        for res in response['Labels']:
            b = res['Label']['Name']
            summary.append(b)
        summaryt = [ (summary.count(x), x) for x in set(summary)]
        print("*****************************************************\n")
        print("SUMMARY: \n\nLabels  detected and its occurences:\n")
        print(summaryt)
        responsej = json.dumps(response, indent=4, sort_keys =True) 
        f = open('job-label-output', 'w')
        f.write(responsej)
        f.close
        print("\n Using default value for result gathering: 1000")
        print("\n ** Full job out in JSON format in file job-label-output **")
        
        
        
    def do_starttrack(self, args):
        """ Tracking video analysis. Usage: starttrack  S3Bucket videoname SNSTopic ARNRole. """
        if len(args) == 0:
            print("Arguments missing for analyzing the video. Needs 4 arguments. Help is your friend.")
        else:
            cid = args.split()
            if len(cid) <4:
                print("Arguments missing. We need 5 arguments")
                return
            print("S3Bucket name: ", cid[0])
            print("Video to analyze: ", cid[1])
            print("SNS ARN", cid[2])
            print("ARN Role",cid[3])
            print("")

            response=client.start_person_tracking(
                    Video={
                        'S3Object': {
                            'Bucket': cid[0],
                            'Name': cid[1],
                        }
                    },
                    NotificationChannel={
                        'SNSTopicArn': cid[2],
                        'RoleArn': cid[3]
                    },
                    JobTag='Jobrekdemo'
                )
            print(response)
            print("--------------------------------------------")
            lastjob=json.dumps(response['JobId'])
            print("JobID generated to track is: ",lastjob)
            f = open('joblogfile', 'a')
            f.write(lastjob)
            f.write(args)
            f.write('\n')
            f.close 
            return

        
    def do_resulttrack(self, args):
        """ Prints the result of the analysis of the  tracking detection job, jobId  is needed, """
        summary = []
        if len(args) == 0:
            lastjob = os.getenv('JOBID')
            print("No jobID given. Need JobId")
            print(response)
        else:
            cid = args.split()
            print("JobID: ", cid[0])
        response = client.get_person_tracking(
            JobId=cid[0],  SortBy='INDEX'
        )
        #Job in progress? Show it and getout
        if not response['Persons']:
            print(json.dumps(response,indent=4,sort_keys=True))
            return
        
        #Job finished
        responsej = json.dumps(response, indent=4, sort_keys =True) 
        print(responsej)
        f = open('job-tracking-output', 'w')
        f.write(responsej)
        f.close
        print("\n Using default value for result gathering: 1000")
        #If here, job is completed, print response.
        long=len(response['Persons'])
        for res in range(0, long):
            b = response['Persons'][res]['Person']['Index']
            print(type(response['Persons'][res])," <--- PPRINT\n")
            c = json.dumps(b)
            print("------------Index detected: ",c," ---------------------")
            print("Timestamp: ",response['Persons'][res].get('Timestamp',"No time"))
            print("--------------------------------------------------------")
            print("")
            summary.append(c)


        summaryt = [ (summary.count(x), x) for x in set(summary)]
        print("*****************************************************")
        print("SUMMARY: Indexes detected and its occurrences:")
        print(summaryt)
        print("\n Using default value for result gathering: 1000")
        print("\n ** Full job out in JSON format in file job-faces-output **")
        return
    
        
        

if __name__ == '__main__':
    prompt = MyPrompt()
    prompt.prompt = '> '
    prompt.cmdloop('\n\n\n ______     ______     __  __     ______        ______     __         __    \n/\  == \   /\  ___\   /\ \/ /    /\  __ \      /\  ___\   /\ \       /\ \   \n\ \  __<   \ \  __\   \ \  _"-.  \ \ \/\ \     \ \ \____  \ \ \____  \ \ \  \n \ \_\ \_\  \ \_____\  \ \_\ \_\  \ \_____\     \ \_____\  \ \_____\  \ \_\ \n  \/_/ /_/   \/_____/   \/_/\/_/   \/_____/      \/_____/   \/_____/   \/_/ \n\n\n**** SIMPLE AWS REKOGNITION CLI ****    [Built for Demo purposes]. \n\n ******** IMPORTANT ********\n Before using this CLI:, \n1) Configure AWS CLI tool with your region.\n2) Make sure your instance has a role to allow rekognition and S3 permission \n3) You need a bucket with the images, videos and a SNS Topic ARN and its ServiceRole ARN ready, all in the same region. Enjoy!!\n\nType "help" for available commands. Got questions? ask @dbernao.\n')
