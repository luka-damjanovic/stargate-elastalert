#### ELASTALERT ORACLIZE VERSION ####

The Oraclize version of elastalert is installed in the /etc directory, and all
of the configurable rules along with any other modifications to the source
should be done in there, as that is the code that will be directly run by
systemd based on the service description.


### Changes ###

The base elastalert Alert object now inherits from the oraclize module created
to allow for more control over notification frequency, message contents, etc.

When new rules are added, and further changes/modifications are needed to get
the rule to perform in a desired state the /etc/elastalert/elastalert/oraclize.py
script is where those changes should go. There are existing methods in there
that can be used as a template when adding new rules.

This module extends notifications to be cached and allow for historical
comparisons between them to refrain from alerting to frequently or for example
alert based on some integer interval so we don't spam recipients.

Adding a new control method the @cached decorator must be specified to
be able to use caching with the new rule. A path to the new cache must be
given as a parameter and will write new data to the cache when the function
returns:

    @cached('/etc/elastalert/cache/MYOBJ.obj')
    def _format_my_new_alert(self, alert_text_values, alert_arg_mapping):
        ...
        ...


### Alerts ###

Alerts are maintained in /etc/elastalert/alerts/ since that is what is
configured in the /etc/elastalert/config.yaml to be the rule lookup directory.

Existing rules:

    cpu usage  - currently monitor's Rinkeby server for any cpu spikes over 
                 a max threshold of 90% for over a minute timeframe

    memory usage - currently monitor's Rinkeby server for any memory spikes
                   in swap memory usage that are above a 90% usage threshold

    disk usage - currenlty monitor's Rinkeby server for any disk usage spikes
                 set to 90% of the servers available disk space

New rules:

    When adding a new rule, it will have to follow basic outlines posted in
    elastalert's docs (https://elastalert.readthedocs.io/en/latest/)
    depending on the rule type chosen, certain paramerters will need to be
    defined.

    Setting a rule based upon the existing ones will be useful for simple
    logical comparisons on metrics we currently are exposed to us through
    elasticsearch. (e.g. system metrics from metricbeat, filtered log counts,
    from filebeat, etc).
    For these you will need to set query options followed by a max/min
    thresholds for the metrics. Also within the rules you will specify the
    alerts text and text parameters which should be included in the message
    e.g: system.cpu.total.pct when it is above the configured threshold


### SYSTEMD ###

I implemented a simple new /etc/elastalert/elastalert.service script for allowing
systemd to ensure the service will be running if any unexpected crashes occur in
the python thread.

This script also defines how the service starts, hence why I have listed the
paths to files because they are reflected in the ExecStart stanza in the service
script.

### TESTING NEW ALERTS BY HAND ###

Testing new rules should be done by setting the actions in the script to debug
solely, excluding any slack/email notifications as these should be included
when the rules are in a stable state. Running the rules by hand using the
following command will allow for more verbose debugging of new rules:

python /etc/elastalert/elastalert/elastalert.py --config /etc/elastalert/config.yaml --start NOW

*** Where NOW is the current datetime in the format: %Y-%%m-%dT%%H:%M:%S
	which you can get from the following command: date +'%Y-%%m-%dT%%H:%M:%S'
***

More verbosity can be added by specifying the --es_debug option which will
print out the query as well as the query output from elasticsearch.
