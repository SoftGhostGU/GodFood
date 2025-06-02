import { Component } from 'react'
import ThirdPartKey from '../utils/const.js'
import { View, Map, Input, Icon } from '@tarojs/components'
import amapFile from '../utils/amap-wx.130.js'
import './locationMap.scss'

let myAmapFun

interface State {
  latitude: number,
  longitude: number,
  markers: any[],
  searchResults: any[],
  pois: any[],
  showSearch: boolean,
  keyword: string,
}

/// 修改和选择已有修理厂
export default class LocationMap extends Component<{}, State> {
  state: State = {
    latitude: 23.099994,
    longitude: 113.324520,
    searchResults: [],
    showSearch: false,
    keyword: '',
    pois: [],
    markers: []
  }

  componentWillMount = () => {
    /// 初始化高德地图
    myAmapFun = new amapFile.AMapWX({ key: ThirdPartKey.amapKey_wx })
  }

  componentDidMount() {
    /// 获取精准定位
    let that = this
    myAmapFun.getRegeo({
      success: (data) => {
        // markersData = data.markers;
        console.log(data)
        var {
          latitude,
          longitude
        } = that.state
        let { pois, addressComponent } = data[0].regeocodeData
        latitude = data[0].latitude
        longitude = data[0].longitude
        let marker
        if (pois.length > 0) {
          marker = this.getMarker(pois[0])
          /// 默认选中第0组数据
          pois[0].checked = true
        }
        /// 加上省市区 让地址变得长一些
        pois.map(item => {
          item.realaddress = addressComponent.province + addressComponent.city + addressComponent.district + item.address
        })
        var markers: any = []
        if (marker) {
          markers.push(marker)
        }
        this.setState({ latitude, longitude, pois, markers })
      },
      fail: (err) => {
        console.log(err)
      }
    })
  }

  onInputValueChange = (e) => {
    const { value } = e.detail
    // console.log(value)
    if (value.length == 0) {

      this.setState({
        searchResults: [],
        // showSearch: false,
        keyword: '',
      }, () => {
        // Taro.hideKeyboard()
      });
      return
    }
    /// 搜索POI功能
    myAmapFun.getInputtips({
      keywords: value,
      // city: '杭州',
      // location: '120.299221,30.419153',
      success: (data) => {
        console.log(data)
        if (data && data.tips) {
          this.setState({
            keyword: value,
            searchResults: data.tips
          });
        }
      }
    })
  }

  getMarker = (item: any) => {
    /// 点击重新设置气泡
    let locations = item.location.split(',')
    let longitude = locations[0]
    let latitude = locations[1]

    let marker = {
      id: item.id,
      latitude,
      longitude,
      name: item.name,
      width: 20,
      height: 30,
    }
    return marker
  }

  /// 点击搜索结果
  onResultItemClick = (item) => {
    /// 根据搜索结果 重新定位
    /// 将经纬度字符串转换出来
    try {
      let locations = item.location.split(',')
      let longitude = locations[0]
      let latitude = locations[1]

      let marker = {
        id: item.id,
        latitude,
        longitude,
        name: item.name,
        width: 20,
        height: 30,
      }

      /// 根据经纬度 获取周边的poi
      myAmapFun.getPoiAround({
        location: item.location,
        success: (data) => {
          console.log(data)
          let pois = data.poisData || []
          if (pois.length > 0) {
            pois[0].checked = true
          }
          pois.map(res => {
            res.realaddress = res.pname + res.cityname + res.adname + res.address
          })

          this.setState({
            keyword: '',
            showSearch: false,
            markers: [marker],
            latitude, longitude,
            searchResults: [],
            pois
          })
        },
        fail: (err) => {
          this.setState({
            keyword: '',
            showSearch: false,
            markers: [marker],
            searchResults: [],
            latitude, longitude

          })
        }
      })
    } catch (error) {
      let e = {
        detail: {
          value: item.name,
        }
      }
      this.onInputValueChange(e)
    }
  }

  onPoiItemClick = (item: any, index: number) => {
    /// 点击重新设置气泡
    let marker = this.getMarker(item)
    let { pois } = this.state
    /// 清空所有的显示 
    pois.map(data => {
      data.checked = false
      return item
    })
    pois[index].checked = true
    this.setState({
      markers: [marker],
      pois
    })

    // console.log(item.realaddress)
    // Taro.eventCenter.trigger('selectAddress', {
    //   type: 'factory',
    //   address: item.realaddress,
    // })
    // Taro.navigateBack({})
  }

  cancleSearch = () => {
    this.setState({
      showSearch: false,
      keyword: '',
      searchResults: [],
    })
  }

  onClear = () => {
    this.setState({
      keyword: '',
      searchResults: [],
    })
  }


  render() {

    let { latitude, longitude, markers, searchResults, showSearch, keyword, pois } = this.state
    return (
      <View className='selectFactoryAddress'>
        <View className='container'>
          {/* 地图 */}
          <View className='map-wrap'>
            <Map
              id="mapId"
              className="map"
              latitude={latitude || 0}
              longitude={longitude}
              showLocation={true}
              markers={markers}
            ></Map>
          </View>
          {/* 搜索 */}
          <View className='search-wrap'>
            <View className='input-wrap'>
              <Icon className='searchIcon' type='search' size='12' />
              <Input className='input'
                placeholder='请输入关键字搜索'
                value={keyword}
                onInput={this.onInputValueChange.bind(this)}
                onFocus={() => this.setState({ showSearch: true })}
              ></Input>
              {
                keyword.length > 0 && <View className='clear-img' onClick={() => this.onClear()}>
                  <Icon type='clear' size='12' />
                </View>
              }
            </View>
            {
              showSearch && <View className='search' onClick={() => this.cancleSearch()}>取消</View>
            }
          </View>

          {/* poi内容 */}
          <View className='poi-wrap' >
            {
              pois.map((item, index) => {
                return (
                  <View className={`poi-item ${item.checked ? 'active' : ''}`} key={index} onClick={() => this.onPoiItemClick(item, index)}>
                    <View className='content'>
                      <View className='name'>{item.name}</View>
                      <View className='address'>{item.realaddress}</View>
                    </View>
                  </View>
                )
              })
            }
          </View>

          {
            showSearch && <View className='search-result-wrap'>
              {
                searchResults.map((item, index) => {
                  return (<View className='result-item' key={index} onClick={() => this.onResultItemClick(item)}>
                    <View className='name'>{item.name}</View>
                    <View className='detail'>{item.district + item.address}</View>
                  </View>)
                })
              }
              {
                searchResults.length == 0 && <View className='nodata-wrap'>
                  <View>暂无数据</View>
                </View>
              }
            </View>
          }
        </View >
      </View >
    )
  }
}

