class LogData:
    def __init__(
        self,
        export_logs_root_path: str = "../experiment_logs",
        export_logs_folder_prefix: str = "exp",
        export_logs_at_end_of_execution: bool = False,
        export_logs_append_to_last_log_folder_instead_of_create: bool = True,
        logs_root_folder: str = "Logs",
        logs_folders: list[str] = None,
    ) -> None:
        self.export_logs_root_path = export_logs_root_path
        self.export_logs_folder_prefix = export_logs_folder_prefix
        self.export_logs_at_end_of_execution = export_logs_at_end_of_execution
        self.export_logs_append_to_last_log_folder_instead_of_create = (
            export_logs_append_to_last_log_folder_instead_of_create
        )
        self.logs_root_folder = logs_root_folder
        self.logs_folders = (
            logs_folders
            if logs_folders is not None
            else [
                "Epsilon Logs",
                "Message Logs",
                "Training Logs",
                "Training Time Logs",
                "Weight Logs",
            ]
        )

    def __str__(self):
        return (
            f"LogData(export_logs_root_path={self.export_logs_root_path}, "
            f"export_logs_folder_prefix={self.export_logs_folder_prefix}, "
            f"export_logs_at_end_of_execution={self.export_logs_at_end_of_execution}, "
            f"export_logs_append_to_last_log_folder_instead_of_create={self.export_logs_append_to_last_log_folder_instead_of_create}, "
            f"logs_root_folder={self.logs_root_folder}, "
            f"logs_folders={self.logs_folders})"
        )
