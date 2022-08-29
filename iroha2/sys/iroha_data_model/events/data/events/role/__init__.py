from ......rust import Enum, make_struct, make_tuple, Dict
RoleEvent = Enum[("Created", "iroha_data_model.role.Id"), ("Deleted", "iroha_data_model.role.Id")] 
