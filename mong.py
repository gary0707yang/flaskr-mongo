import pymongo
from bson.objectid import ObjectId

class Db:
    def __init__(self, url='mongodb://localhost:27017/', database='test'):
          self.connection = pymongo.MongoClient(url)
          self.db = self.connection[database]
          self.image_collection = self.db['sample']
          self.user_colletion = self.db['user']

    def get_all_image(self):
        images = self.image_collection.find()

        return images


    def get_all_tags(self):
        tags = {}
        images = self.image_collection.find()
        for image in images:
            for tag in image['tags']:
                if tag in tags.keys():
                    tags[tag] +=1
                else:
                    tags[tag] = 1
        
        return tags

    def get_images_by_tag(self, tag):
        images = self.image_collection.find({'tags':tag})

        return images

    def get_image_filename_by_id(self, id):
        image = self.image_collection.find_one({'_id':ObjectId(id)})
        # print(image)
        return image