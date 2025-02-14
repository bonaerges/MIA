import toml, sys, os
from openai import OpenAI

def load_api_key(toml_file_path="secrets.toml"):
    try:
        with open(toml_file_path, 'r') as file:
            data = toml.load(file)
    except FileNotFoundError:
        print(f"File not found: {toml_file_path}", file=sys.stderr)
        return
    except toml.TomlDecodeError:
        print(f"Error decoding TOML file: {toml_file_path}", file=sys.stderr)
        return
    # Set environment variables
    for key, value in data.items():
        os.environ[key] = str(value)

def obtener_prompt(nombre_archivo, **kwargs):
    with open(nombre_archivo, 'r', encoding="utf-8") as archivo:
        contenido = archivo.read()
        # Comprueba si se pasaron argumentos a la función
        if kwargs:
            # Formatea el contenido con las variables pasadas solo si hay argumentos
            prompt_formateado = contenido.format(**kwargs)
        else:
            # Si no hay argumentos, devuelve el contenido directamente
            prompt_formateado = contenido
    return prompt_formateado

def llamada_modelo(system, prompt, client, model="openai/gpt-4-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def main():
    load_api_key()
    # Inicializar el cliente de OpenAI
    BASE_URL = "https://openrouter.ai/api/v1"
    API_KEY = os.environ.get("OPENROUTER_API_KEY")

    client = OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY
    )

    # Cargar todos los archivos de la forma response{id}.md de la carpeta actual
    archivos = [f for f in os.listdir() if os.path.isfile(f) and f.startswith("response") and f.endswith(".md")]

    # Por cada archivo, leer el contenido y almacenarlo en la variable instrucciones
    instrucciones = ""
    for archivo in archivos:
        with open(archivo, 'r') as file:
            instrucciones = file.read()
        print(f"Procesando {archivo}")
        triplets = llamada_modelo(obtener_prompt("systemPrompt.txt"), instrucciones, client)
        # Guardar triplets en un archivo txt, que tenga el nombre triplets{nombre de archivo}.txt
        with open(f"triplets{archivo[8:-3]}.txt", "w") as file:
            file.write(triplets)

if __name__ == "__main__":
    main()