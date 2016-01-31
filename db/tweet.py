from mongoengine import Document, IntField, StringField, FloatField, DictField, ListField


class Tweet(Document):
    def __init__(self, **kwargs):

        super(Tweet, self).__init__()

        _id = kwargs.pop('id', None)
        if _id:
            kwargs['tweet_id'] = _id

        for k, v in kwargs.iteritems():
            print k, v
            if isinstance(v, dict):
                self.__setattr__(k, DictField(**v))
            elif isinstance(v, str):
                self.__setattr__(k, StringField(v))
            elif isinstance(v, unicode):
                self.__setattr__(k, StringField(v.encode('utf-8')))
            elif isinstance(v, float):
                self.__setattr__(k, FloatField(v))
            elif isinstance(v, int):
                self.__setattr__(k, IntField(v))
            elif isinstance(v, type(None)):
                self.__setattr__(k, None)
            elif isinstance(v, list):
                self.__setattr__(k, ListField(v))

            else:
                raise ValueError('Value "{0}" of type "{1}" not accepted'.format(str(v), type(v)))


