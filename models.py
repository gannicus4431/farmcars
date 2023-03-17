from bson import ObjectId
from pydantic import Field, BaseModel
from typing import Optional

# While the fields are simple and we are not going to perform some fine-tuned validation, 
# you will immediately face a problem that should be tackled upfront. 
# We have seen that MongoDB uses something called ObjectId, assigns every document a property _id, 
# and stores documents as BSON (binary JSON). 
# FastAPI, or Python really, encodes and decodes data as JSON strings and that is also what will 
# be expected in our frontend. As I have seen, there are basically two possibilities: 
# to preserve the ObjectId field in MongoDB or to transform it into a string representation that 
# will ensure uniqueness. While both options are viable, I will opt for the latter as it is simpler 
# to set up and it will require us to write less code for serializing objects. See the example here:

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# The preceding code basically just defines our own implementation of ObjectId functionality, 
# along with some validation and the update of the schema in order to output strings. 
# Now, we just have to extend Pydantic’s BaseModel with the PyObjectId that we just created and 
# use it as the basis for all of our models:

class MongoBaseModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    class Config:
        json_encoders = {ObjectId: str}

# It is important to note that we have used the alias option in order to be able to use the field 
# in our Pydantic model. Having our version of the BaseModel (called MongoBaseModel) ready, 
# we can now proceed and define our other fields:

class CarBase(MongoBaseModel):    
    brand: str = Field(..., min_length=3)
    make: str = Field(..., min_length=3)
    year: int = Field(...)
    price: int = Field(...)
    km: int = Field(...)
    cm3: int = Field(...)


# While we’re at it, let’s define the model for our update route – we want to be able to provide 
# just a single field and update only that field in the model. We have seen how pydantic manages 
# to achieve this:

class CarUpdate(MongoBaseModel):    
    price: Optional[int] = None
class CarDB(CarBase):
    pass