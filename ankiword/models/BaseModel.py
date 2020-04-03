class BaseModel:
    def __init__(self, name):
        self.name = name
        self.fields = {}

    def get_fields(self):
        return self.fields()

    def set_fields(self, field_name, field_val):
        setattr(self.fields, field_name, field_val)

    def add_model_name(self, model_name):
        self.fields["modelName"] = model_name
