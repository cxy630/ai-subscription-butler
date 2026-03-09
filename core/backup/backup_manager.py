"""
数据备份和恢复管理器
"""

import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import shutil


class BackupManager:
    """数据备份管理器"""

    def __init__(self, data_dir: str = "data", backup_dir: str = "backups"):
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def create_full_backup(self, user_id: str = None) -> Dict[str, Any]:
        """创建完整备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if user_id:
            backup_name = f"backup_{user_id}_{timestamp}"
        else:
            backup_name = f"backup_full_{timestamp}"

        # 准备备份数据
        backup_data = {
            "backup_info": {
                "created_at": datetime.now().isoformat(),
                "backup_type": "user" if user_id else "full",
                "user_id": user_id,
                "version": "1.0.0"
            },
            "data": {}
        }

        # 读取数据文件
        data_files = ["users.json", "subscriptions.json", "conversations.json"]

        for filename in data_files:
            file_path = self.data_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                        # 如果指定了用户ID，只备份该用户的数据
                        if user_id and filename != "users.json":
                            if filename == "subscriptions.json":
                                data = [item for item in data if item.get("user_id") == user_id]
                            elif filename == "conversations.json":
                                data = [item for item in data if item.get("user_id") == user_id]
                        elif user_id and filename == "users.json":
                            data = [item for item in data if item.get("id") == user_id]

                        backup_data["data"][filename] = data
                except Exception as e:
                    print(f"读取 {filename} 失败: {e}")
                    backup_data["data"][filename] = []

        # 保存备份文件
        backup_file = self.backup_dir / f"{backup_name}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)

        # 创建压缩备份
        zip_file = self.backup_dir / f"{backup_name}.zip"
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(backup_file, backup_file.name)

        return {
            "success": True,
            "backup_file": str(backup_file),
            "zip_file": str(zip_file),
            "backup_name": backup_name,
            "size": backup_file.stat().st_size,
            "created_at": datetime.now().isoformat()
        }

    def restore_from_backup(self, backup_file: str, merge: bool = False) -> Dict[str, Any]:
        """从备份恢复数据"""
        backup_path = Path(backup_file)

        if not backup_path.exists():
            return {
                "success": False,
                "error": "备份文件不存在"
            }

        try:
            # 读取备份文件
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

            backup_info = backup_data.get("backup_info", {})
            data = backup_data.get("data", {})

            restored_files = []

            # 恢复数据文件
            for filename, file_data in data.items():
                target_file = self.data_dir / filename

                if merge and target_file.exists():
                    # 合并模式：读取现有数据并合并
                    with open(target_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)

                    # 合并逻辑（基于ID去重）
                    if isinstance(existing_data, list) and isinstance(file_data, list):
                        existing_ids = {item.get("id") for item in existing_data if "id" in item}
                        new_items = [item for item in file_data if item.get("id") not in existing_ids]
                        merged_data = existing_data + new_items
                    else:
                        merged_data = file_data

                    with open(target_file, 'w', encoding='utf-8') as f:
                        json.dump(merged_data, f, ensure_ascii=False, indent=2)
                else:
                    # 覆盖模式：直接写入
                    with open(target_file, 'w', encoding='utf-8') as f:
                        json.dump(file_data, f, ensure_ascii=False, indent=2)

                restored_files.append(filename)

            return {
                "success": True,
                "backup_info": backup_info,
                "restored_files": restored_files,
                "restored_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def list_backups(self) -> list:
        """列出所有备份"""
        backups = []

        for backup_file in self.backup_dir.glob("*.json"):
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                    backup_info = backup_data.get("backup_info", {})

                backups.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "size": backup_file.stat().st_size,
                    "created_at": backup_info.get("created_at"),
                    "backup_type": backup_info.get("backup_type"),
                    "user_id": backup_info.get("user_id"),
                    "version": backup_info.get("version")
                })
            except Exception as e:
                print(f"读取备份文件 {backup_file} 失败: {e}")

        # 按创建时间降序排序
        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return backups

    def delete_backup(self, backup_name: str) -> bool:
        """删除备份"""
        backup_file = self.backup_dir / f"{backup_name}.json"
        zip_file = self.backup_dir / f"{backup_name}.zip"

        deleted = False

        if backup_file.exists():
            backup_file.unlink()
            deleted = True

        if zip_file.exists():
            zip_file.unlink()
            deleted = True

        return deleted

    def export_backup_data(self, backup_file: str) -> Optional[bytes]:
        """导出备份数据（ZIP格式）"""
        backup_path = Path(backup_file)

        if not backup_path.exists():
            return None

        # 如果是JSON文件，查找对应的ZIP
        if backup_path.suffix == ".json":
            zip_path = backup_path.with_suffix(".zip")
            if zip_path.exists():
                with open(zip_path, 'rb') as f:
                    return f.read()

        # 如果是ZIP文件，直接读取
        if backup_path.suffix == ".zip":
            with open(backup_path, 'rb') as f:
                return f.read()

        return None

    def import_backup_file(self, uploaded_file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """导入备份文件"""
        try:
            # 保存上传的文件
            import_path = self.backup_dir / filename

            with open(import_path, 'wb') as f:
                f.write(uploaded_file_bytes)

            # 如果是ZIP文件，解压
            if filename.endswith('.zip'):
                with zipfile.ZipFile(import_path, 'r') as zipf:
                    zipf.extractall(self.backup_dir)

                # 找到解压的JSON文件
                json_filename = filename.replace('.zip', '.json')
                json_path = self.backup_dir / json_filename

                if json_path.exists():
                    return {
                        "success": True,
                        "backup_file": str(json_path),
                        "message": "备份文件导入成功"
                    }

            # 如果是JSON文件，直接使用
            elif filename.endswith('.json'):
                return {
                    "success": True,
                    "backup_file": str(import_path),
                    "message": "备份文件导入成功"
                }

            return {
                "success": False,
                "error": "不支持的文件格式"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"导入失败: {str(e)}"
            }

    def get_backup_statistics(self) -> Dict[str, Any]:
        """获取备份统计信息"""
        backups = self.list_backups()

        total_size = sum(b.get("size", 0) for b in backups)
        backup_types = {}

        for backup in backups:
            backup_type = backup.get("backup_type", "unknown")
            backup_types[backup_type] = backup_types.get(backup_type, 0) + 1

        return {
            "total_backups": len(backups),
            "total_size": total_size,
            "backup_types": backup_types,
            "latest_backup": backups[0] if backups else None,
            "oldest_backup": backups[-1] if backups else None
        }


# 全局备份管理器实例
backup_manager = BackupManager()


if __name__ == "__main__":
    # 测试备份管理器
    print("测试备份管理器...")

    # 创建完整备份
    result = backup_manager.create_full_backup()
    print(f"\n创建备份: {result}")

    # 列出所有备份
    backups = backup_manager.list_backups()
    print(f"\n备份列表 ({len(backups)} 个):")
    for backup in backups:
        print(f"  - {backup['filename']} ({backup['size']} bytes)")

    # 统计信息
    stats = backup_manager.get_backup_statistics()
    print(f"\n备份统计: {stats}")