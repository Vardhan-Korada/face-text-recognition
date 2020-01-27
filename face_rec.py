# Python SDK for Amazon
import boto3
import os
import pytesseract
from PIL import Image


#Constants
ID_FILE_PATH = "/home/vardhan/Chandu-Vardhan/Face_Recognition/face_ids.txt"
SOURCE_IMAGE_PATH = "/home/vardhan/Chandu-Vardhan/Face_Recognition/faces/source27.jpg"


#Loading the face_ids and their names
f = open(ID_FILE_PATH,"r")
ids = f.read()
if ids == "":
    face_ids = {}
else:
    face_ids = eval(ids)
f.close()


#Function for creating a new collection
def create_collection(collection_id):
    res = boto3.client("rekognition").create_collection(CollectionId=collection_id)
    print(res["StatusCode"])


#Function for deleting a collection
def delete_collection(collection_id):
    res = boto3.client("rekognition").delete_collection(CollectionId=collection_id)
    print(res["StatusCode"])


#Function for adding a face to the collection
def index_faces(collection_id,image_path):
    try:
        with open(image_path,"rb") as image: 
            res = boto3.client("rekognition").index_faces(
                CollectionId=collection_id,
                Image = {"Bytes":image.read()}
            )
            return res["FaceRecords"][0]["Face"]["FaceId"]
    except:
        pass


#Function with more suitable name for adding a face
def add_face(collection_id,image_path):
    return index_faces(collection_id,image_path)
            

#Function for comparing the source image with database
def search_face(collection_id,threshold,image_path):
    try:
        with open(image_path,"rb") as image:
            new_res = boto3.client("rekognition").detect_faces(
                Image={"Bytes":image.read()}
                )
            if len(new_res["FaceDetails"]) == 0:
                return -9999
            image.close()
        with open(image_path,"rb") as image:
            res = boto3.client("rekognition").search_faces_by_image(
                CollectionId=collection_id,
                FaceMatchThreshold=threshold,
                Image={"Bytes":image.read()}
                )
            res = res["FaceMatches"]
            if len(res) == 0:
                print("No matches found...")
                return 0
            print(len(res),"matches found with ...")
            for i in range(len(res)):
                print(str(i+1)+".","Similarity:",res[i]["Similarity"])
                print(str(i+1)+".","Confidence:",res[i]["Face"]["Confidence"])
                print("It may be "+face_ids[res[i]["Face"]["FaceId"]])
                say_it("It may be "+face_ids[res[i]["Face"]["FaceId"]]+" with "+str(round(res[i]["Similarity"]))+" percent similarity")
            return len(res)
    except:
        print("Image path doesn't exists")


def add_new_face(collection_id,path):
    id = add_face(collection_id,path)
    face_ids[id] = input("Enter a name: ")
    f = open(ID_FILE_PATH,"w")
    f.write(str(face_ids))
    f.close()


def detect_text(path):
    try:
        with open(path,"rb") as image:
            res = boto3.client("rekognition").detect_text(
                Image = {"Bytes":image.read()}
                )
            res = res["TextDetections"]
            detected_texts = []
            for i in range(len(res)):
                sent = res[i]["DetectedText"]
                if res[i]["Type"] == "WORD":
                    continue
                detected_texts.append(sent+" ")
            return detected_texts
    except:
        print("Text processing failed..")


def tes_detect_text(path):
    try:
        res = pytesseract.image_to_string(Image.open(path))
        say_it(res)
    except:
        print("Text processing failed..")


def say_it(sent):
    res = boto3.client("polly").synthesize_speech(
        VoiceId="Joanna",
        OutputFormat="mp3",
        Text=sent
        )
    file = open("speech.mp3","wb")
    file.write(res["AudioStream"].read())
    os.system("mpg123 "+"speech.mp3")
    file.close()


if __name__ == "__main__":
    # delete_collection("Faces")
    # create_collection("Faces")
    # for i in range(1,5):
    #     path = "/home/vardhan/Chandu-Vardhan/Face_Recognition/faces/source"+str(i)+".jpg"
    #     index_faces("Faces",path)
    path = SOURCE_IMAGE_PATH
    text = detect_text(path)
    #tes_detect_text(path)
    matches = search_face("Faces",92,path)
    if len(text) == 0:
        print("No text is present")
        say_it("No text present in the image")
    else:
        tot = ""
        for sent in text:
            tot += sent
        print(tot)
        say_it(tot)
    #Adding a new face to the collection
    if matches == -9999:
        print("No face is present in the image...")
        say_it("No face is present in the image...")
    elif matches == 0:
        ans = input("Do you want to create a new record for the new face?: ")
        if ans in "YyYesyesYES":
            add_new_face("Faces",path)
        else:
            pass
        print("Job Done...")
        
