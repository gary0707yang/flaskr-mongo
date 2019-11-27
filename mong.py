import pymongo
from bson.objectid import ObjectId

class Db:
    # 初始化mongodb数据库
    def __init__(self, url='mongodb://localhost:27017/', database='test', image_collection='sample'):
          self.connection = pymongo.MongoClient(url)
          self.db = self.connection[database]
          self.image_collection = self.db[image_collection]
          self.user_colletion = self.db['user']

    #查找所有图片,直接返回数据库对象,包含多个对象
    def get_all_image(self):
        images = self.image_collection.find()

        return images

    #返回所有tag列表和所包含图片数量
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

    #根据tag查找图片
    def get_images_by_tag(self, tag):
        images = self.image_collection.find({'tags':tag})

        return images

    #根据id返回指定图片
    def get_image_filename_by_id(self, id):
        image = self.image_collection.find_one({'_id':ObjectId(id)})
        # print(image)
        return image

    #为图片插入标签
    def insert_image_tag(self, id, tag):
        image = self.get_image_filename_by_id(id)
        
        #检测标签是否存在
        if tag not in image['tags']:
            image['tags'].append(tag)
            self.image_collection.update_one({'_id':ObjectId(id)}, { "$set": {'tags':image['tags']} })
        
        # print(image)

    # 增加新的图片对象, 返回图片id
    # TODO 增加多个图片
    def add_new_image(self, image_info):
        return self.image_collection.insert_one(image_info)
