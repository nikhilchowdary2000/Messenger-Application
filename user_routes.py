from fastapi import APIRouter , Depends
from config.db import users_collection
from bson import ObjectId
from config.db import messages_collection
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt





user = APIRouter()



#Create User
@user.post("/user")
async def create_user(name : str , email : str , password : str):
    if users_collection.find_one({"email": email}):
            return "User with this email already exists"
    result = users_collection.insert_one({"name": name, "email": email, "password": password})
    return {"id": str(result.inserted_id),"name":name , "email":email}


#View User

@user.get("/users/{id}")
async def get_user(id: str):
    user = users_collection.find_one({"_id": ObjectId(id)})
    if user:
        return {"id": str(user["_id"]), "name": user["name"], "email": user["email"]}
    else:
        return "The ID provided has no data"
    
#Update User

@user.put("/update")
async def update_user(id : str , name : str , email : str , password : str):
     if users_collection.find_one({"_id" : ObjectId(id)}):
          result = users_collection.update_one({"_id": ObjectId(id)}, {"$set": {"name": name, "email": email, "password": password}})
          return {"id": id,"name":name , "email":email , "password" : password}
     else:
          return "the data is not found to update"
          
#login user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl= '/token')

@user.post("/token")
async def token (form_data : OAuth2PasswordRequestForm = Depends()):
   user = users_collection.find_one({"email" : form_data.username , "password" : form_data.password})
   if not user:
       return "user not found"
   access_token = jwt.encode({"sub" : form_data.username},"secret_key",algorithm = "HS256")
   return {'access_token' :access_token , "token_type" : "bearer"}



#Create Message

@user.post("/message")
async def create_message(message: str, token: str = Depends(oauth2_scheme)):
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        user_id = payload["sub"]
        user = users_collection.find_one({"email": user_id})
        if not user:
            return "User not found"
        result = messages_collection.insert_one({
    
            "email": user_id,
            "message": message,
            "timestamp": datetime.now(),
            "likes": [],
            "comments": []
        })
        return {"message_id": str(result.inserted_id)}

#Find Message

@user.get("/message/find{id}")
async def find_message(message_id : str):
    users = messages_collection.find_one({"_id" : ObjectId(message_id)})
    if users:
        return {"id": str(users["_id"]),"user_id" : str(users["user_id"]), "message": users["message"], "timestamp": users["timestamp"]}


# Create Comment
@user.post("/comment")
async def create_comment(message_id: str, comment: str, token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
    user_id = payload["sub"]
    user = users_collection.find_one({"email": user_id})

    if not user:
        return "User not found"
    message = messages_collection.find_one({"_id": ObjectId(message_id)})
    if not message:
        return "Message not found"

    comment_details = {
        "user_id": user["_id"],
        "comment": comment,
        "timestamp": datetime.now()
    }

    result = messages_collection.update_one(
        {"_id": ObjectId(message_id)},
        {"$push": {"comments": comment_details}}
    )

    return "Comment created successfully"

#Like a Message

@user.post("/like")
async def like_message(message_id: str, token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
    user_id = payload["sub"]
    user = users_collection.find_one({"email": user_id})

    if not user:
        return "User not found"
    message = messages_collection.find_one({"_id": ObjectId(message_id)})
    if not message:
        return "Message not found"

   
    result = messages_collection.update_one({"_id": ObjectId(message_id)}, {"$addToSet": {"likes": {"user_id": user["_id"], "timestamp": datetime.now()}}})

    if result.modified_count == 1:
        return {"message": "Message liked successfully"}
    else:
        return "Error"

#details of likes
    
@user.get("/messages/{message_id}/likes")
async def get_likes(message_id: str):

    message = messages_collection.find_one({"_id": ObjectId(message_id)})
    if not message:
        return "Message not found"
    likes = message.get("likes", [])
    
    result = []
    for like in likes:
        user = users_collection.find_one({"_id": like["user_id"]})
        result.append({"user_id": str(like["user_id"]), "user": user["name"], "timestamp": like["timestamp"]})
    return result


#Get count for likes

@user.get("/likescount")
async def count_likes(message_id: str):
    message = messages_collection.find_one({"_id": ObjectId(message_id)})
    if not message:
        return "Message not found"
    likes_count = len(message.get("likes", []))
    return {"message_id": message_id, "likes_count": likes_count}

#View all the messages


@user.get("/messages")
async def get_messages(year: int = None):
   
    messages = messages_collection.find({"timestamp": {"$gte": datetime(year, 1, 1), "$lt": datetime(year + 1, 1, 1)}})
    result = []
    for message in messages:
        result.append({"id": str(message["_id"]),"message": message["message"], "timestamp": message["timestamp"]})
    return result

#View Comments

@user.get("/viewcomments")
async def view_comments(message_id: str):
    user = messages_collection.find_one({"_id" : ObjectId(message_id)})
    if not user:
        return "Message not found"
    result = []
    for comment in user.get("comments", []):
        result.append({
            "user_id": str(comment["user_id"]),
            "comment": comment["comment"],
            "timestamp": comment["timestamp"]
        })
    return result
