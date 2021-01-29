{% extends base_script %}
{% block project_header %}
{{ super() }}
# set walltime limit to 24 hours from now (minus 10 minutes)
# https://hoomd-blue.readthedocs.io/en/v2.9.3/restartable-jobs.html#cleanly-exit-before-the-walltime-limit
export HOOMD_WALLTIME_STOP=$((`date +%s` + 24 * 3600 - 10 * 60))
{% endblock %}
