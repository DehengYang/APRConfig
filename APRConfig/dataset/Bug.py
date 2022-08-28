class Bug(object):
    def __init__(self, dataset, project, bug_id, patch_diff=None):
        self.project = project
        self.bug_id = bug_id
        self.dataset = dataset

        self.name = f"{dataset.name}_{project}_{bug_id}"

        self.__working_dir = None
        self.__patch_diff = patch_diff

    def set_working_dir(self, working_dir):
        self.__working_dir = working_dir

    def get_working_dir(self):
        assert self.__working_dir is not None, "please checkout first"
        return self.__working_dir

    def set_patch_diff(self, patch_diff):
        self.__patch_diff = patch_diff

    def get_patch_diff(self):
        return self.__patch_diff

    def __str__(self):
        return self.name

    def get_proj_id(self):
        return f"{self.project}_{self.bug_id}"