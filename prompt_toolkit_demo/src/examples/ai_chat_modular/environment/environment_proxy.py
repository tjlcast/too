import os


class EnvironmentProxy:
    def get_current_dir(self):
        current_dir = os.getcwd()
        return current_dir

    def get_current_time(self):
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return current_time

    def get_current_working_directory(self):
        current_path = os.getcwd()
        return f"# Current Workspace Directory ({current_path}) Files\n" + self.__get_current_working_directory(current_path)

    def __get_current_working_directory(self, pwd: str = None) -> str:
        """
        返回当前工作目录的详细信息，包括文件和文件夹列表
        递归遍历所有子目录并以相对路径形式返回所有文件
        """
        try:
            if pwd:
                current_path = pwd
            else:
                current_path = os.getcwd()
            result = ""

            # 定义黑名单，包含需要跳过的目录和文件
            blacklist = {
                '.git', '__pycache__', '.vscode', 'node_modules', '.idea',
                '.DS_Store', 'Thumbs.db',  'site-packages', '__MACOSX', '.venv', 'target'
            }

            # 递归遍历所有文件和目录
            all_files = []
            for root, dirs, files in os.walk(current_path):
                # 检查当前目录是否在黑名单中
                root_rel_path = os.path.relpath(root, current_path)
                if root_rel_path != ".":
                    root_dirs = root_rel_path.split(os.sep)
                    if any(dir_name in blacklist for dir_name in root_dirs):
                        continue

                # 过滤目录（不在黑名单中的目录才会被遍历）
                dirs[:] = [d for d in dirs if d not in blacklist]

                # 计算相对于当前目录的路径
                rel_root = os.path.relpath(root, current_path)

                # 添加目录路径
                for dir_name in dirs:
                    if rel_root == ".":
                        # all_files.append(f"{dir_name}/")
                        pass
                    else:
                        all_files.append(f"{rel_root}/{dir_name}/")

                # 添加文件路径（跳过黑名单中的文件）
                for file_name in files:
                    # 检查文件是否在黑名单中
                    if file_name in blacklist:
                        continue

                    if rel_root == ".":
                        all_files.append(file_name)
                    else:
                        all_files.append(f"{rel_root}/{file_name}")

            # 排序并添加到结果中
            for file_path in sorted(all_files):
                # 添加 "./" 前缀以明确表示相对路径
                result += f"{file_path}\n"

            return result
        except Exception as e:
            return f"无法获取目录信息: {str(e)}"


"""
Run command: python -m src.examples.ai_chat_modular.environment.environment_proxy
"""
if __name__ == "__main__":
    # 测试 EnvironmentProxy 类
    env_proxy = EnvironmentProxy()

    print("测试 get_current_dir:")
    print(env_proxy.get_current_dir())
    print()

    print("测试 get_current_time:")
    print(env_proxy.get_current_time())
    print()

    print("测试 get_current_working_directory:")
    print(env_proxy.get_current_working_directory())
