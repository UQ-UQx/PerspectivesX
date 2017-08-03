var React = require('react')
var ReactDOM = require('react-dom')

var ActivityList = React.createClass({
    loadActivityFromServer: function(){
        $.ajax({
            url: this.props.url,
            datatype: 'json',
            cache: false,
            success: function(data) {
                this.setState({data: data});
            }.bind(this)
        })
    },

    getInitialState: function() {
        return {data: []};
    },

    componentDidMount: function() {
        this.loadActivityFromServer();
        setInterval(this.loadActivityFromServer,
                    this.props.pollInterval)
    },
    render: function() {
        if (this.state.data) {
            console.log('DATA!')
            var activityNodes = this.state.data.map(function(activity){
                return <li> {activity.title} </li>
            })
        }
        return (
            <div>
                <h1>Hello React!</h1>
                <ul>
                    {activityNodes}
                </ul>
            </div>
        )
    }
})

ReactDOM.render(<ActivityList url='/api/Activity' pollInterval={1000} />,
    document.getElementById('container'))