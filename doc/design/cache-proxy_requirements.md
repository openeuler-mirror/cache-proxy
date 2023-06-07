# cache-proxy需求文档

## 需求背景/意图

当前openEuler社区的upstream源码包直接放在src-openeuler社区代码仓，不仅不符合工程原则，也导致源码压缩包无法进行版本控制，难以确定压缩包的来源和创建方式，可能导致安全隐患。我们需要将源码压缩包从src-openeuler社区代码仓移除，从上游直接获取。但是这样又会因为上游网络问题、版本管控机制差异，造成版本错误、下载速度慢、甚至下载失败的情况，因此我们需要建立一个upstream代理的源码缓存中心仓。这样当我们需要下载文件时，首先会从缓存中检查文件是否存在，如果存在则直接下载缓存的文件，如果不存在则从源地址下载并保存到缓存中，以备将来使用。

## User Story

- 作为开发人员，我希望能通过缓存代理服务下载文件，以便节省带宽和提高下载速度。
- 作为开发人员，我希望缓存代理服务能自动检测文件是否已存在于缓存中，以便我无需手动操作。

- 作为开发人员，我希望upstream出现下载失败的情况，能有限次重试，失败后能及时通知运维人员处理。
- for upstream url 404, however src-openeuler has tar
  - create HTTP web server or huaweicloud artifact as 中心仓 (vs 分布式缓存)
  - upload src-openeuler tar to it
  - change spec Source0 to our HTTP web server URL
  - keep md5sum 保证内容没变
- 作为安全人员，我希望缓存代理服务具备基本网关治理能力，实现负载均衡、流量控制、访问次数限制。
- avoid DDOS, limit URL? filter out obvious mp3/video
- on local storage fail, remove own IP from DNS

- 如果没有指定OBS配置，仅以本地目录作为缓存--cache proxy服务应该具备，即使没有OBS存储，也能启动并将本地目录作为缓存的能力。
- 将OBS的缓存文件&upstream的url<缓存不存在>Redirect给client
- OBS预留缓存清理策略
- 本地建立一个内存cache<map>，不需每次都从OBS中查询某个文件是否存在，设定cache刷新策略
- "docker-compose up"命令启动应用，cache proxy应用本身不对外暴露，必须经由nginx(gateway)转发

bottleneck at network traffic for out
DNS (负载均衡)
IP1 IP2 IP3
per-vm virtual gateway module (per-client-ip 流量控制, 次数)
vm1 vm2 vm3
S3/OBS shared

distributed

GET url 
net bw 100MBPS
disk 100MB/s performance is not bottleneck

if OBS/local has file:
	return data
else
	REDIRECT client to upstream # streaming
	start download to local in background
	(optional) upload to OBS

DNS 
service make simple

nginx + 云盘

proxy with cache
client -> squid/upstream-proxy ->  upstream-proxy 
upstream-proxy

squid (multi layer: HW cache, cluster cache, china cache in huaweicloud) 
- tar
- jar
- not support S3/OBS storage
nginx
- has OBS backend

why OBS?
- careless on disk corruption, data loss, distributed, out of service
- disk full? 80%
- DDOS

/result
hourly cleanup remove oldest files

distributed in world
not in one huawei area
OBS

run 3 standalone services
- each with local fs cache, or OBS
- storage size for 1 OS

1w Source0 x10 versions
10T sata disk

dns to them

func-diff

I want download or make sure xxxx is cached
wget --http-proxy=upstream-proxy URL 

需求：support http/https/ftp
需求：各处复用
- 三方开发者 (run 1 public service in huaweicloud)
- 构建系统 内部缓存 (run 1 per build cluster)
docker service
  --mount data-cache-dir
需求：华为云部署	OBS
需求：蓝区/各lab部署	local file

## 约束考量

- 缓存空间有限，需要设计合理的缓存过期策略，以及不相关文件的及时清理。
- 支持600+的并发下载量，需要考虑多实例负载均衡、后端缓存的并发支持和出口带宽限制。
- 根据client地域差异，需要考虑网络延迟和失败情况。

## 可选方案
1. squid 
2. 自建服务

1. **本地缓存**：将文件保存在本地硬盘上。优点是访问速度快，不需要网络连接。缺点是空间有限，需要手动管理缓存。
2. **云存储服务**：利用如AWS S3或者华为云OBS等云服务提供的存储，将文件保存在云端。优点是空间充足，可以自动管理缓存，访问速度相对较快，容灾能力强。缺点是需要网络连接，可能会有一些费用。

考虑到长期的维护和稳定性，我们选择使用华为云OBS云服务。

## 架构设计

1. 创建一个缓存管理器，该管理器能与云存储服务交互，进行文件的上传和下载。
2. 当用户请求一个文件时，缓存管理器首先检查文件是否已存在于云存储服务中。
3. 如果文件存在，缓存管理器将重定向缓存url给client。
4. 如果文件不存在，缓存管理器将从源地址下载文件，返回文件给client，然后并行将文件上传到云存储服务。

## 工作量(人天)

1. 缓存管理器的开发和测试（3人天）
2. 与云存储服务的集成（2人天）
3. 源地址下载的功能开发和测试（2人天）
4. 总体测试和文档编写（1人天）

总计：8人天

## 决策依据

- **Who**：社区用户、开发人员、社区维护人员
- **When**：当使用eulerMaker构建软件包前，需要获取上游源码包时
- **What**：开发一个upstream缓存代理服务，供eulerMaker下载和查询缓存包，以加速下载和屏蔽上游社区网络问题
- **How**：首先检查文件是否已存在于云存储服务中，如果存在则直接下载，如果不存在则从源地址下载并保存到云存储服务
- **Why**：1、优化src-openeuler工程配置； 2、加速下载；3、屏蔽上游社区的版本变更、网络问题
- **Options/Tradeoffs**：本地缓存 vs 云存储服务。本地缓存空间有限，访问速度快，容灾能力弱；云存储服务空间充足，容灾能力强，可能需要网络连接。
- **Facts/Reasoning**：由于云存储服务的可扩展性和易管理性，我们选择使用云存储服务。
- **Examples/Abstraction**：例如，当我们需要从https://www.kernel.org/pub/software/scm/git/git-2.39.1.tar.xz 下载文件时，我们可以通过缓存代理服务来提高下载速度和节省带宽。
