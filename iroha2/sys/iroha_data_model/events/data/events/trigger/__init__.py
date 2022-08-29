from ......rust import Enum, make_struct, make_tuple, Dict
TriggerEvent = Enum[("Created", "iroha_data_model.trigger.Id"), ("Deleted", "iroha_data_model.trigger.Id"), ("Extended", "iroha_data_model.trigger.Id"), ("Shortened", "iroha_data_model.trigger.Id")] 
