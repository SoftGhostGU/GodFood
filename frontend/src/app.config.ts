export default defineAppConfig({
  pages: [
    'pages/index/index',
    'pages/myInfo/index',
    'pages/dashBoard/index'
  ],
  tabBar: {
    list: [
      {
        pagePath: 'pages/index/index',
        text: '首页',
        iconPath: './assets/tabbar/like.png',
        selectedIconPath: './assets/tabbar/like_selected.png'
      },
      {
        pagePath: 'pages/dashBoard/index',
        text: '我的订单',
        iconPath: './assets/tabbar/dashBoard.png',
        selectedIconPath: './assets/tabbar/dashBoard_selected2.png'
      },
      {
        pagePath: 'pages/myInfo/index',
        text: '我的信息',
        iconPath: './assets/tabbar/user.png',
        selectedIconPath: './assets/tabbar/user_selected.png'
      }
    ],
    color: '#999999',
    selectedColor: '#1296db',
    backgroundColor: '#ffffff',
    borderStyle: 'black'
  },
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#fff',
    navigationBarTitleText: 'WeChat',
    navigationBarTextStyle: 'black'
  },
  requiredPrivateInfos: [
    "getLocation",
    "chooseLocation"
  ],
  permission: {
    "scope.userLocation": {
      "desc": "你的位置信息将用于小程序位置接口的效果展示"
    }
  }
})
