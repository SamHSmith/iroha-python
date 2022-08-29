from ...rust import Enum, make_struct, make_tuple, Dict
Id = make_struct("Id", [("name", "iroha_data_model.name.Name")])

Trigger = make_struct("Trigger", [("id", "iroha_data_model.trigger.Id"), ("action", "iroha_data_model.trigger.action.Action")])

