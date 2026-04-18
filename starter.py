import subprocess
import os
import json

# Загружаем настройки
with open("config.json", "r") as f:
    config = json.load(f)

ver = config["version"]
ver_dir = os.path.join(".minecraft", "versions", ver)
jar = os.path.join(ver_dir, f"{ver}.jar")

# Собираем classpath
libs_dir = os.path.join(".minecraft", "libraries")
classpath = jar
for root, dirs, files in os.walk(libs_dir):
    for file in files:
        if file.endswith(".jar"):
            classpath += os.pathsep + os.path.join(root, file)

natives = os.path.join(ver_dir, "natives")
os.makedirs(natives, exist_ok=True)

cmd = [
    "java", "-Xmx2G",
    f"-Djava.library.path={natives}",
    "-cp", classpath,
    "net.minecraft.client.main.Main",
    "--username", "PolarPlayer",
    "--uuid", "00000000-0000-0000-0000-000000000000",
    "--accessToken", "00000000-0000-0000-0000-000000000000",
    "--version", ver,
    "--gameDir", os.path.abspath(".minecraft"),
    "--assetsDir", os.path.join(".minecraft", "assets"),
    "--assetIndex", "1.19.4"
]

subprocess.run(cmd)