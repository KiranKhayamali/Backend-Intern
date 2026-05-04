

type Query{
    allPersons(last: int): [Person!]!
    allPosts(last: int): [Post!]!
}

type Mutation{
    createPerson(name: String!, age: Int!): Person!
    updatePerson(id: ID!, name: String, age: Int): Person!
    deletePerson(id: ID!): Person!
}

type Subscription{
    newPerson: Person!
    updatedPerson: Person!
    deletedPerson: Person!
}

type Person{
    id: ID!
    name: String!
    age: Int!
    posts: [Post!]!
}

type Post{
    id: ID!
    title: String!
    author: Person!
}