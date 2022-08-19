{% extends "bridges2.sh" %}
{% block tasks %}
{{ super() -}}
#SBATCH --output=workspace/{{operations[0]._jobs[0]}}/job_%j.o
#SBATCH --error=workspace/{{operations[0]._jobs[0]}}/job_%j.e
#SBATCH -t 48:00:00
{% endblock tasks %}
{% block header %}
{{ super() -}}
{% endblock header %}
