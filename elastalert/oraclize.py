import sys
import logging

log = logging.getLogger('oraclize')

class OraclizeAlerts(object):
    """ This base class consists will be responsible for formatting any Oraclize
        specific alert messages before dispatching to any alert types.
        e.g.
            - converting data types to be more human readable
            - any extensive data comparison that cannot be achieved
              with the basic elastalert yaml config attributes
    """
    def __init__(self):
        self.MESSAGE_TYPE = { "DISK": self._format_disk_alert,
                              "CPU": self._format_cpu_alert,
                              "MEMORY": self._format_memory_alert
                            }

    def format_oraclize_alerts(self, alert_text_values, alert_arg_mapping):
        alert_text = unicode(self.rule.get('alert_text', ''))
        func = [func for substr, func in self.MESSAGE_TYPE.iteritems() if substr in alert_text]
        if len(func) > 0:
            log.info("Formatting alert <%s> with <%s>" % (alert_text, func[0]))
            return func[0](alert_text_values, alert_arg_mapping)

    def _format_disk_alert(self, alert_text_values, alert_arg_mapping):
        used = float(alert_arg_mapping['system.fsstat.total_size.used'])
        total = float(alert_arg_mapping['system.fsstat.total_size.total'])
        avg = (used / total) * 100
        alert_text_values[0] = alert_arg_mapping['beat.hostname']
        alert_text_values[1] = '%.2f%%' % avg
        return alert_text_values

    def _format_cpu_alert(self, alert_text_values, alert_arg_mapping):
        cpu_pct = '%.2f%%' % (alert_text_values[-1] * 100)
        alert_text_values[-1] = cpu_pct
        return alert_text_values

    def _format_memory_alert(self, alert_text_values, alert_arg_mapping):
        swap = float(alert_arg_mapping['system.memory.swap.used.pct']) * 100
        real = float(alert_arg_mapping['system.memory.actual.used.pct']) * 100
        alert_text_values[1:3] = '%.2f%%' % swap, '%.2f%%' % real
        return alert_text_values
