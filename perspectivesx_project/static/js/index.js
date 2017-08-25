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

class EmptySubmissionComponent extends React.Component{
    constructor(){
        super()
    }
    render(){
        <div>
            <p> No submissions items for this perspective</p>
            <a href = "sss"></a>
        </div>
    }
}

class PerspectiveComponent extends React.Component{

    constructor(props) {
        super(props);
        this.state = {items: [], curated: [], perspective: props.perspective, activity: props.activity};
    }

    loadItemsFromServer(){
        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_user_submission_items/"+this.state.activity+"/"+this.state.perspective+"/",
            datatype: 'json',
            cache: false,
            success: function(data) {
                this.setState({items: data});
            }.bind(this)
        });
        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_user_curated_items/"+this.state.activity+"/"+this.state.perspective+"/",
            datatype: 'json',
            cache: false,
            success: function(data) {
                this.setState({curated: data});
            }.bind(this)
        });
    }


    componentDidMount() {
        this.loadItemsFromServer();
        // setInterval(()=>this.loadItemsFromServer(),
        //             this.props.pollInterval);
    }
    render() {
            console.log(this.state.items)
             const listStyleType = {
                listStyleType: 'none'
             };
            const containerStyle ={
                marginLeft: "15px",
                marginRight:"15px"
            };
            var itemNodes = this.state.items.map(function (item) {
                return <ItemComponent item={item}/>

            });

            var curatedNodes = this.state.curated.map(function (curated) {
                return <ItemComponent item={curated}/>
            })
            if(curatedNodes.length>0 && itemNodes.length>0) {
            // if(curatedNodes.length==0) {
            //     curatedNodes = "No curated items from this perspective ! \n Click \"view all\" to start curating. ";
            // }
            // if(itemNodes.length == 0){
            //     itemNodes = "No submissions items for this perspecitve"
                return (
                    <div className = "container-fluid" style = {containerStyle}>
                        <div className = "row">
                            <div className = "col-md-6">
                                <div className = "well">
                                        <p>Submitted for {this.props.name} :</p>
                                        <ul style={listStyleType}>
                                            {itemNodes}
                                        </ul>
                                        <br/>
                                    <a href = {"/perspectivesX/display_perspective_items/" + this.state.perspective+"/"}
                                    className = "btn btn-primary btn-md">View all</a>
                                </div>
                            </div>
                            <div className = "col-md-6">
                                <div className = "well">
                                    <p>Curated for {this.props.name} :</p>
                                    <ul style={listStyleType}>
                                        {curatedNodes}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                )
            }else{
                    if(curatedNodes.length>0){
                        return (
                            <div className = "container-fluid" style = {containerStyle}>
                                <div className = "row">
                                    <div className = "col-md-12">
                                        <div className = "well">
                                            <p>Curated for {this.props.name} :</p>
                                            <ul style={listStyleType}>
                                                {curatedNodes}
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )
                    }else{
                        if(itemNodes.length>0){
                            return(
                                <div className = "container-fluid" style = {containerStyle}>
                                    <div className = "row">
                                        <div className = "col-md-12">
                                            <div className = "well">
                                                <p>Submitted for {this.props.name} :</p>
                                                    <ul style={listStyleType}>
                                                        {itemNodes}
                                                    </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )
                        }
                    }
                    return (
                        <div className = "container-fluid" style = {containerStyle}>
                            <div className = "row">
                                <div className = "col-md-12">
                                    <div className = "well well-sm">
                                        <p style = {{textAlign:"center"}}>No items for {this.props.name} !</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )
            //}
        }
    }
}


class PerspectiveGridComponent extends React.Component{
    constructor(props){
        super(props);
        this.state = {perspectives: []};

    }

    loadPerspectivesFromServer(){
         var cur = this;
        $.ajax({
            url: "/perspectivesX/get_template_items/"+this.props.activity+"/",
            datatype: 'json',
            cache: false,
            success: function(data) {
                this.setState({perspectives: data});
            }.bind(this)
        });
    }

    componentDidMount() {
        this.loadPerspectivesFromServer();
        // setInterval(()=>this.loadPerspectivesFromServer(),
        //             this.props.pollInterval);
    }


    render(){
       if (this.state.perspectives) {
           var perspectiveNodes = this.state.perspectives.map(
               (perspective) => this.mapPerspectives (perspective, this.props.activity)
           );
            return (

                    <div className = "row">

                        <h3>{this.props.name}</h3>
                        {perspectiveNodes}
                    </div>
               )
       }

    }

    mapPerspectives(perspective,activity){
         return  <PerspectiveComponent activity = {this.props.activity} perspective={perspective.id} name = {perspective.name}/>;
    }
}

class ActivityGridComponent extends React.Component{

    constructor(props){
        super(props);
        this.state = {activities: []};
    }

    loadActivitiesFromServer(){
        var cur = this;
        $.ajax({
            url: "/perspectivesX/get_activities/",
            datatype: 'json',
            cache: false,
            success: function(data) {
                this.setState({activities: data});
            }.bind(this)
        });
    }

    componentDidMount() {
        this.loadActivitiesFromServer();
        setInterval(()=>this.loadActivitiesFromServer(),
                    this.props.pollInterval);
    }

    render(){
        if (this.state.activities) {
            const containerStyle ={
                marginLeft: "15px",
                marginRight:"15px"
            };
           var perspectiveGrids = this.state.activities.map(function (activity) {
                    return  <PerspectiveGridComponent activity={activity.id} name = {activity.title}/>

                });
            return (

                    <div className = "container-fluid" style ={containerStyle}>
                        {perspectiveGrids}
                    </div>
               )
       }

    }
}
    ReactDOM.render(<ActivityGridComponent pollInterval={100000000} />, document.getElementById("container"));



