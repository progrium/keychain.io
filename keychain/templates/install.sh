mkdir -p $HOME/.ssh
touch $HOME/.ssh/authorized_keys
{% for key in keys %}
echo "{{key}}" >> $HOME/.ssh/authorized_keys
{% endfor %}
