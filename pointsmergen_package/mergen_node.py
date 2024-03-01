# -*- coding: utf-8 -*- #apply Japanese
import message_filters
from typing import List
import rclpy
from rclpy.clock import Clock, ClockType
from rclpy.time import Duration
from rclpy.context import Context  # ROS2のPythonモジュールをインポート
from rclpy.node import Node
from rclpy.parameter import Parameter # rclpy.nodeモジュールからNodeクラスをインポート
from sensor_msgs.msg import PointCloud2,PointField
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header
import numpy as np
import time 

# 点の座標を定義するフレームの名前
HEADER = Header(frame_id='/map')

# PointCloud2のフィールドの一覧
FIELDS = [
    # 点の座標(x, y, z)
    PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
    PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
    PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
    # 点の色(RGB)
    PointField(name='intensity', offset=12, datatype=PointField.FLOAT32, count=1),
]

class pointsmergenSubPub(Node):


    def __init__(self):
        super().__init__("centerpoints")
        self.pcd_01_sub = message_filters.Subscriber(self, PointCloud2,"/filtered_points_01")
        # self.pcd_02_sub = message_filters.Subscriber(self, PointCloud2,"/points_no_ground_03")
        # self.pcd_03_sub = message_filters.Subscriber(self, PointCloud2,"/points_no_ground_04")
        self.pcd_04_sub = message_filters.Subscriber(self, PointCloud2,"/filtered_points_04")

        pcd_sub_list = [self.pcd_01_sub, self.pcd_04_sub]

        mf = message_filters.ApproximateTimeSynchronizer(pcd_sub_list, 1, 1000000)
        mf.registerCallback(self.listener_callback)
        
        # self.numpy_publisher = self.create_publisher(PointCloud2,'/numpy_points_no_ground', 1)
        self.list_publisher = self.create_publisher(PointCloud2,'/list_filtered_points', 1)
    def listener_callback(self, msg1, msg4): 
        """サブスクライバーのコールバック関数。
        """

        # list
        """listの方が早い"""
        start_time_list = time.time()
        cloud1 = np.array(point_cloud2.read_points_list(msg1, field_names=['x', 'y', 'z', "intensity"], skip_nans=True, uvs=[]))
        # cloud2 = np.array(point_cloud2.read_points_list(msg2, field_names=['x', 'y', 'z', "intensity"], skip_nans=True, uvs=[]))
        # cloud3 = np.array(point_cloud2.read_points_list(msg3, field_names=['x', 'y', 'z', "intensity"], skip_nans=True, uvs=[]))
        cloud4 = np.array(point_cloud2.read_points_list(msg4, field_names=['x', 'y', 'z', "intensity"], skip_nans=True, uvs=[]))
        cloud_list=cloud1.tolist()
        cloud_list.extend((cloud4.tolist()))
        mergen_pcd = cloud_list
        pcd_msg = point_cloud2.create_cloud(header=HEADER,fields=FIELDS,points=np.array(mergen_pcd))
        print("list",time.time() - start_time_list) # 0.01
        self.list_publisher.publish(pcd_msg)



def main(args=None):
    rclpy.init(args=args)          # rclpyモジュールの初期化
    pointsmergen_SubPub = pointsmergenSubPub() # ノードの作成
    rclpy.spin(pointsmergen_SubPub)      # コールバック関数が呼び出し
    pointsmergenSubPub.destory_node()   # ノードの破壊
    rclpy.shutdown()               # rclpyモジュールの終了処理

if __name__ == '__main__':
    main()