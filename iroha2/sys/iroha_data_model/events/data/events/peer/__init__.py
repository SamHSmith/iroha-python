from ......rust import Enum, make_struct, make_tuple, Dict
PeerEvent = Enum[("Added", "iroha_data_model.peer.Id"), ("Removed", "iroha_data_model.peer.Id")] 
