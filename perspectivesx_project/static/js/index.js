var React = require('react');
var ReactDOM = require('react-dom');

class ItemComponent extends React.Component{

        //React component to display a single submission Item.
        //Displays the text and author of a Perspective Item


    constructor(props){
        super(props);
        this.state = {item: props.item}

    }

    render(){
        const liStyle = {
            borderStyle: 'outset',
            backgroundColor:'lightgrey',
            marginBottom: '10px'
        };
        return <li  key={this.state.item.id} style = {liStyle} > Item: {this.state.item.item}<br/>
            Author: {this.state.item.description.split("from")[1]}<br/> </li>
        }

}

class PerspectiveComponent extends React.Component{

    constructor() {
        super();
        this.state = {items: [], curated: []};
    }

    loadItemsFromServer(){
        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_user_submission_items/",
            datatype: 'json',
            cache: false,
            success: function(data) {
                this.setState({items: data});
            }.bind(this)
        });
        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_user_curated_items/",
            datatype: 'json',
            cache: false,
            success: function(data) {
                this.setState({curated: data});
            }.bind(this)
        });
    }


    componentDidMount() {
        this.loadItemsFromServer();
        setInterval(()=>this.loadItemsFromServer(),
                    this.props.pollInterval);
    }
    render() {
        if (this.state.items) {
            console.log("items")
            console.log(this.state.items);
            console.log("curated")
            console.log(this.state.curated);
            var perspectiveNodes = this.state.items.map(function(item){
                return <ItemComponent item = {item}/>
            });
            var curatedNodes = this.state.curated.map(function(curated){
                return <ItemComponent item = {curated}/>
            })
        }
        const listStyleType = {
                listStyleType: 'none'
            };

        return (
            <div>
                < h1>Hello React!</h1>
                <p>Submitted:</p>
                <ul style = {listStyleType}>
                    {perspectiveNodes}
                </ul>
                <p>Curated:</p>
                <ul style = {listStyleType}>
                    {curatedNodes}
                </ul>
            </div>
        )
    }
}

    ReactDOM.render(<PerspectiveComponent pollInterval={5000} />, document.getElementById("container"));



