# -*- coding: utf-8 -*-


class TriggerMixin(object):
    def drop_triggers(self):
        for trigger_name in self.list_triggers():
            self.drop_trigger(trigger_name)

    def drop_trigger(self, name):
        raise NotImplementedError

    def list_triggers(self):
        raise NotImplementedError

