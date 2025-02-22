import sgtk
import os


class Flow(object):
    """
    An object representing the SG connection
    """

    @classmethod
    def connect(cls, script_key=None, user=False, path=None):
        """
        Create a connection to Shotgrid

        @param script_key: str, name of key (e.g. Nuke, Maya, etc)
        @param user: bool, should we connect as the current desktop user?
        @param path: str, path to get the toolkit instance from
        @return: None
        """

        flow = cls()

        # Assume we are in a DCC grab the engine
        flow.get_engine()

        if flow.engine is None:
            # We are not working with an engine. Try to get the user.
            sg_user = None
            if user:
                # we are connecting as a user
                sg_user = flow.get_user()
                sgtk.set_authenticated_user(sg_user)
                flow.api = sg_user.create_sg_connection()

            else:
                # we are connecting as a script
                if script_key is None:
                    # ask for a key if we don't have one
                    print("Please provide a script key!")
                else:
                    key = f"SCRIPT_KEY_{script_key.upper()}"
                    sa = sgtk.authentication.ShotgunAuthenticator()
                    sg_user = sa.create_script_user(
                        api_script=key, api_key=os.environ.get(key)
                    )

            if path is not None:
                flow.toolkit_from_path(path)

        return flow

    def __init__(self):
        self.api = None
        self.engine = None
        self.engine_info = None
        self.tk = sgtk

    def get_engine(self):
        """
        If we are in a DCC get the engine
        """
        self.engine = sgtk.platform.current_engine()
        # first try to get the connection from the engine
        if self.engine is not None:
            self.api = self.engine.shotgun
            self.tk = self.engine.sgtk
            self.engine_info = self.engine.get_metrics_properties()

    def get_user(self):
        """
        Get the user from SG Desktop
        """
        sa = sgtk.authentication.ShotgunAuthenticator()
        user = sa.get_user()
        return user

    def toolkit_from_path(self, path):
        """
        Get the toolkit from the provided path
        :param path: str, path inside the project
        """
        self.tk = sgtk.sgtk_from_path(path)


flow = Flow.connect(user=True)
