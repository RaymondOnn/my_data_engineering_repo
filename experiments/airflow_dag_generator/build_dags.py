from jinja2 import Environment, FileSystemLoader
import yaml
import os

file_dir = os.path.abspath(f'{__file__}/../.')
env = Environment(loader=FileSystemLoader(file_dir))
template = env.get_template('./templates/template.jinja2')

for file in os.listdir(f'{file_dir}/configs'):
    filename = file.split('.')[0]
    if file.endswith('.yaml'):
        with open(f'{file_dir}/configs/{file}', 'r') as config_file:
            cfg = yaml.safe_load(config_file)

            dag_filename = f'{file_dir}/dags/{filename[0]}/{filename}.py'
            dag_dir = os.path.dirname(dag_filename)
            if not os.path.exists(dag_dir):
                os.makedirs(dag_dir)
            with open(f'{file_dir}/dags/{filename[0]}/{filename}.py', 'w') as dag_file:
                output = template.render(cfg)
                dag_file.write(output)
                print(f'Dag file generated: {dag_filename}')
                print(output)
