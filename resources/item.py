from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help="Cannot be blank or zero."
        )
    parser.add_argument('store_id',
        type=int,
        required=True,
        help="Every store needs a store id."
        )
    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
                return item.json()
        return {'message': '{} Not Found'.format(name)},404

    def post(self,name):
        if ItemModel.find_by_name(name):
              return {'message': "An item named {} already exists.".format(name)}, 400 
        data = Item.parser.parse_args()
#        data = request.get_json()
        item = ItemModel(name, data['price'], data['store_id'])
        try:
                item.save_to_db()
        except:
                return{"message":"Error inserting item: {}".format(name)},500
        return item.json(), 201

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
                item.delete_from_db()
        return {'message': "Item {} deleted".format(name)}

    def put(self, name):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)
        
        if item is None:
               item = ItemModel(name, data['price'], data['store_id'])        # doesn't use **args
        else:
               item.price = data['price']
               
        item.save_to_db()
        return item.json()


class ItemList(Resource):
    def get(self):
        return {'items':[x.json() for x in ItemModel.query.all()]}
        #return {'items': list(map(lambda x: x.json(), ItemModel.query.all()))}