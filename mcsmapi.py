
import asyncio
import aiohttp
from typing_extensions import Self
from typing import Dict, List
from yarl import URL


class StatusCodeException(Exception):
    def __init__(self, code: int):
        super().__init__('Unexcept status code: {}'.format(code))
        self.status_code = code


class McsmApi(object):
    '''
    参数参见 http://docs.mcsmanager.com/
    '''

    session: aiohttp.ClientSession
    api: URL
    apikey: str

    def __init__(self, api: str, apikey: str) -> None:
        self.api = URL(api) / "api"
        self.apikey = apikey
        self.session = aiohttp.ClientSession()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.session.close()

    async def async_get(self, content_type: str = "application/json", **kwargs):
        if "method" not in kwargs:
            kwargs["method"] = "GET"
        async with self.session.request(**kwargs) as resp:
            if resp.status == 200:
                try:
                    return await resp.json(content_type=content_type)
                except aiohttp.client_exceptions.ContentTypeError:
                    return await resp.json(content_type=content_type)
            else:
                raise StatusCodeException(resp.status)


class Panel():
    # 面板通用设置

    def __init__(self, mcsmapi: McsmApi):
        self.api = mcsmapi.api
        self.apikey = mcsmapi.apikey
        self.session = mcsmapi.session
        self.async_get = mcsmapi.async_get

    async def overview(self):
        url = self.api / "overview"
        return await self.async_get(url=url, params={"apikey": self.apikey})

    async def servce_remote_services_system(self):
        url = self.api / "service" / "remote_services_system"
        return await self.async_get(url=url, params={"apikey": self.apikey})

    async def overview_setting(self):
        url = self.api / "overview" / "setting"
        return await self.async_get(url=url, params={"apikey": self.apikey})

    async def update_overview_setting(self, data: dict):
        url = self.api / "overview" / "setting"
        return await self.async_get(content_type="text/plain", method="PUT", url=url, data=data, params={"apikey": self.apikey})


class User():

    def __init__(self, mcsmapi: McsmApi):
        self.api = mcsmapi.api
        self.apikey = mcsmapi.apikey
        self.session = mcsmapi.session
        self.async_get = mcsmapi.async_get

    async def create_user(self, username: str, password: str, permission: int):
        url = self.api / "auth"
        data = {
            "username": username,
            "password": password,
            "permission": permission
        }
        return await self.async_get(method="POST", url=url, json=data, params={"apikey": self.apikey})

    async def delete_user(self, uuid: str | List):
        if type(uuid) == str:
            uuid = [uuid]
        url = self.api / "auth"
        return await self.async_get(method="DELETE", url=url, json=uuid, params={"apikey": self.apikey})

    async def overview_user(self):
        url = self.api / "auth" / "overview"
        return await self.async_get(url=url, params={"apikey": self.apikey})

    async def get_user_info(self, uuid: str = None, advanced: bool = True):
        url = self.api / "auth"
        params = {"advanced": advanced, "apikey": self.apikey}
        if uuid is not None:
            params["uuid"] = uuid
        return await self.async_get(url=url, params=params)

    async def search_user(self, username: str, page: int = 1, page_size: int = 10):
        url = self.api / "auth" / "search"
        params = {"userName": username,
                  "page": page,
                  "page_size": page_size,
                  "apikey": self.apikey,
                  }
        return await self.async_get(url=url, params=params)

    async def update_self_user(self, username: str, password: str, permission: int):
        url = self.api / "auth" / "update"
        return await self.async_get(method="PUT", url=url, params={"apikey": self.apikey}, json={
            "userName": username,
            "passWord": password,
            "permission": permission
        })

    async def update_user(self, uuid: str, permission: int, instances: List[Dict]):
        url = self.api / "auth"
        return await self.async_get(method="PUT", url=url, params={"apikey": self.apikey}, json={
            "uuid": uuid,
            "config": {
                "permission": permission,
                "instances": instances}
        })


class Remote():

    def __init__(self, mcsmapi: McsmApi):
        self.api = mcsmapi.api
        self.apikey = mcsmapi.apikey
        self.session = mcsmapi.session
        self.async_get = mcsmapi.async_get

    async def add_remote_service(self, apikey: str, port: str, ip: str, remark: str):
        url = self.api / "service" / "remote_service"
        return await self.async_get(method="POST", url=url, params={"apikey": self.apikey}, json={
            "apiKey": apikey,
            "port": port,
            "ip": ip,
            "remarks": remark
        }
        )

    async def delete_remote_service(self, uuid: str):
        url = self.api / "service" / "remote_service"
        return await self.async_get(method="DELETE", url=url, params={"apikey": self.apikey, "uuid": uuid})

    async def edit_remote_service(self, uuid: str, **kwargs):
        # kwargs = {apikey: str = None, ip: str = None, port: str = None, remarks: str = None}
        url = self.api / "service" / "remote_service"
        return await self.async_get(method="PUT", url=url, params={"apikey": self.apikey, "uuid": uuid}, json=kwargs)

    async def get_all_remote_services(self):
        url = self.api / "service" / "remote_services"
        return await self.async_get(url=url, params={"apikey": self.apikey})

    async def get_list_remote_services(self):
        url = self.api / "service" / "remote_services_list"
        return await self.async_get(url=url, params={"apikey": self.apikey})

    async def reconnect_remote_service(self, uuid: str):
        url = self.api / "service" / "link_remote_service"
        return await self.async_get(url=url, params={"apikey": self.apikey, "uuid": uuid})


class Instance():
    def __init__(self, mcsmapi: McsmApi):
        self.api = mcsmapi.api
        self.apikey = mcsmapi.apikey
        self.session = mcsmapi.session
        self.async_get = mcsmapi.async_get

    async def get_instance(self, uuid: str, remote_uuid: str):
        url = self.api / "instance"
        return await self.async_get(url=url, params={"apikey": self.apikey, "uuid": uuid, "remote_uuid": remote_uuid})

    async def search_instance(self, instance_name: str, remote_uuid: str, page: int = 1, page_size: int = 10):
        url = self.api / "service" / "remote_service_instances"
        return await self.async_get(url=url, params={"apikey": self.apikey, "remote_uuid": remote_uuid, "instance_name": instance_name, "page": page, "page_size": page_size})

    async def create_instance(self, remote_uuid: str, config: dict):
        # config 见 http://docs.mcsmanager.com/#/instance/create_instance
        url = self.api / "instance"
        return await self.async_get(method="POST", url=url, params={"remote_uuid": remote_uuid, "apikey": self.apikey}, json=config)

    async def edit_instance(self, uuid: str, remote_uuid: str, config: dict):
        # config 见 http://docs.mcsmanager.com/#/instance/create_instance
        url = self.api / "instance"
        return await self.async_get(method="PUT", url=url, params={"uuid": uuid, "remote_uuid": remote_uuid, "apikey": self.apikey}, json=config)

    async def delete_instance(self, remote_uuid: str, instances: List[dict]):
        # instances ={
        # "uuids": ["e11b018bc6514c7385bf923a3e048772"], // 实例UUID
        # "deleteFile": false // 是否删除文件
        # }
        # 见 http://docs.mcsmanager.com/#/instance/delete_instance
        url = self.api / "instance"
        return await self.async_get(method="DELETE", url=url, params={"remote_uuid": remote_uuid, "apikey": self.apikey}, json=instances)

    async def open_instance(self, uuid: str, remote_uuid: str):
        url = self.api / "protected_instance" / "open"
        return await self.async_get(url=url, params={"uuid": uuid, "remote_uuid": remote_uuid, "apikey": self.apikey})

    async def stop_instance(self, uuid: str, remote_uuid: str):
        url = self.api / "protected_instance" / "stop"
        return await self.async_get(url=url, params={"uuid": uuid, "remote_uuid": remote_uuid, "apikey": self.apikey})

    async def kill_instance(self, uuid: str, remote_uuid: str):
        url = self.api / "protected_instance" / "kill"
        return await self.async_get(url=url, params={"uuid": uuid, "remote_uuid": remote_uuid, "apikey": self.apikey})

    async def restart_instance(self, uuid: str, remote_uuid: str):
        url = self.api / "protected_instance" / "restart"
        return await self.async_get(url=url, params={"uuid": uuid, "remote_uuid": remote_uuid, "apikey": self.apikey})

    async def run_command_instance(self, uuid: str, remote_uuid: str, command: str):
        url = self.api / "protected_instance" / "command"
        return await self.async_get(url=url, params={"uuid": uuid, "remote_uuid": remote_uuid, "command": command, "apikey": self.apikey})

    async def get_instance_log(self, uuid: str, remote_uuid: str):
        url = self.api / "protected_instance" / "outputlog"
        return await self.async_get(url=url, params={"uuid": uuid, "remote_uuid": remote_uuid, "apikey": self.apikey})

    async def instance_file_exists(self, uuid: str, remote_uuid: str, files: List[str]):
        url = self.api / "protected_instance" / "process_config" / "list"
        return await self.async_get(url=url, params={"uuid": uuid, "remote_uuid": remote_uuid, "apikey": self.apikey}, json={"files": files})

# 不准备提供 Schedule 和 File 的封装, Meaningless


async def main():
    # async with McsmApi("http://127.0.0.1:23333", "apikey") as mcsmapi:
    #     print(await Panel(mcsmapi).overview())
    pass


if __name__ == "__main__":
    asyncio.run(main())
