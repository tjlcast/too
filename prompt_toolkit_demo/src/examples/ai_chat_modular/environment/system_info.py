import os
import platform
import getpass

def __get_shell():
    """获取默认shell"""
    if platform.system() == "Windows":
        return os.environ.get("COMSPEC", "cmd.exe")
    else:
        return os.environ.get("SHELL", "/bin/sh")

def __to_posix(path):
    """将路径转换为posix格式"""
    return path.replace("\\", "/")

def get_system_info_section(cwd: str) -> str:
    """
    获取系统信息部分文本
    
    Args:
        cwd (str): 当前工作目录路径
        
    Returns:
        str: 包含系统信息的格式化字符串
    """
    details = f"""====
    
SYSTEM INFORMATION

Operating System: {platform.platform()}
Default Shell: {__get_shell()}
Home Directory: {__to_posix(os.path.expanduser('~'))}
Current Workspace Directory: {__to_posix(cwd)}

The Current Workspace Directory is the active VS Code project directory, and is therefore the default directory for all tool operations. New terminals will be created in the current workspace directory, however if you change directories in a terminal it will then have a different working directory; changing directories in a terminal does not modify the workspace directory, because you do not have access to change the workspace directory. When the user initially gives you a task, a recursive list of all filepaths in the current workspace directory ('/test/path') will be included in environment_details. This provides an overview of the project's file structure, offering key insights into the project from directory/file names (how developers conceptualize and organize their code) and file extensions (the language used). This can also guide decision-making on which files to explore further. If you need to further explore directories such as outside the current workspace directory, you can use the list_files tool. If you pass 'true' for the recursive parameter, it will list files recursively. Otherwise, it will list files at the top level, which is better suited for generic directories where you don't necessarily need the nested structure, like the Desktop."""
    
    return details

if __name__ == "__main__":
    print(get_system_info_section(os.getcwd()))