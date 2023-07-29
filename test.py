from superagi.tools.external_tools.rabbitmq.rabbitmq_tool import RabbitMQTool

# Create an instance of the class
tool = RabbitMQTool(
    description="test rabbitmq tool",
    config=config,
    name="test rabbitmq tool"
    )

# Check that the attributes are correctly initialized
assert tool.config.rabbitmq_server == 'localhost', f'Expected rabbitmq_server to be localhost, but got {tool.config.rabbitmq_server}'
assert tool.config.rabbitmq_username == 'guest', f'Expected rabbitmq_username to be guest, but got {tool.config.rabbitmq_username}'
assert tool.config.rabbitmq_password == 'guest', f'Expected rabbitmq_password to be guest, but got {tool.config.rabbitmq_password}'

print('All attributes are correctly initialized!')